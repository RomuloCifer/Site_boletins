"""
Middleware de Segurança Personalizado para o Sistema de Notas
"""

import time
import logging
from django.core.cache import cache
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils import timezone
from django.conf import settings
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """
    Middleware de segurança com proteções personalizadas
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Configurações de segurança
        self.max_login_attempts = getattr(settings, 'MAX_LOGIN_ATTEMPTS', 5)
        self.lockout_duration = getattr(settings, 'LOCKOUT_DURATION_MINUTES', 15)
        self.session_timeout = getattr(settings, 'SESSION_TIMEOUT_MINUTES', 60)
        
    def __call__(self, request):
        # Verificações antes da view
        if self.is_blocked_ip(request):
            return HttpResponseForbidden("IP temporariamente bloqueado devido a atividade suspeita.")
        
        if self.check_session_timeout(request):
            return self.handle_session_timeout(request)
        
        # Registrar atividade do usuário
        if request.user.is_authenticated:
            self.update_user_activity(request)
        
        # Processar requisição
        response = self.get_response(request)
        
        # Verificações após a view
        self.check_suspicious_activity(request, response)
        
        return response
    
    def is_blocked_ip(self, request):
        """
        Verifica se o IP está temporariamente bloqueado
        """
        ip_address = self.get_client_ip(request)
        cache_key = f'blocked_ip_{ip_address}'
        
        blocked_until = cache.get(cache_key)
        if blocked_until:
            if timezone.now() < blocked_until:
                return True
            else:
                cache.delete(cache_key)
        
        return False
    
    def check_session_timeout(self, request):
        """
        Verifica se a sessão do usuário expirou por inatividade
        """
        if not request.user.is_authenticated:
            return False
        
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity_time = datetime.fromisoformat(last_activity)
            
            if timezone.now() - last_activity_time > timedelta(minutes=self.session_timeout):
                return True
        
        return False
    
    def handle_session_timeout(self, request):
        """
        Lida com timeout de sessão
        """
        logout(request)
        
        if request.path.startswith('/api/') or request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({
                'error': 'Sessão expirada por inatividade',
                'redirect': '/teacher-portal/login/'
            }, status=401)
        
        return redirect('teacher_portal:login')
    
    def update_user_activity(self, request):
        """
        Atualiza timestamp de última atividade do usuário
        """
        request.session['last_activity'] = timezone.now().isoformat()
        
        # Também atualizar no cache para monitoramento
        cache_key = f'user_activity_{request.user.id}'
        cache.set(cache_key, timezone.now(), 3600)  # 1 hora
    
    def check_suspicious_activity(self, request, response):
        """
        Detecta atividade suspeita e toma ações preventivas
        """
        # Detectar múltiplas tentativas de acesso negado
        if response.status_code == 403:
            self.handle_forbidden_access(request)
        
        # Detectar tentativas de SQL injection ou XSS
        if self.detect_malicious_patterns(request):
            self.block_ip_temporarily(request)
            logger.warning(f"Atividade suspeita detectada do IP {self.get_client_ip(request)}")
    
    def handle_forbidden_access(self, request):
        """
        Lida com tentativas de acesso não autorizado
        """
        ip_address = self.get_client_ip(request)
        cache_key = f'forbidden_attempts_{ip_address}'
        
        attempts = cache.get(cache_key, 0) + 1
        cache.set(cache_key, attempts, 3600)  # 1 hora
        
        if attempts >= 10:  # 10 tentativas de acesso negado
            self.block_ip_temporarily(request, duration_minutes=30)
            logger.warning(f"IP {ip_address} bloqueado por múltiplas tentativas de acesso negado")
    
    def detect_malicious_patterns(self, request):
        """
        Detecta padrões maliciosos na requisição
        """
        malicious_patterns = [
            'union select',
            'drop table',
            '<script',
            'javascript:',
            'eval(',
            'setTimeout(',
            '../../../',
            'cmd.exe',
            '/etc/passwd'
        ]
        
        # Verificar parâmetros GET e POST
        request_data = str(request.GET) + str(request.POST)
        request_data = request_data.lower()
        
        for pattern in malicious_patterns:
            if pattern in request_data:
                return True
        
        return False
    
    def block_ip_temporarily(self, request, duration_minutes=None):
        """
        Bloqueia IP temporariamente
        """
        duration = duration_minutes or self.lockout_duration
        ip_address = self.get_client_ip(request)
        
        blocked_until = timezone.now() + timedelta(minutes=duration)
        cache_key = f'blocked_ip_{ip_address}'
        cache.set(cache_key, blocked_until, duration * 60)
        
        logger.warning(f"IP {ip_address} bloqueado por {duration} minutos")
    
    def get_client_ip(self, request):
        """
        Obtém o IP real do cliente
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class RateLimitMiddleware:
    """
    Middleware para limitação de taxa de requisições
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Limites de taxa (requisições por minuto)
        self.rate_limits = {
            'login': 5,  # 5 tentativas de login por minuto
            'import': 2,  # 2 importações por minuto
            'api': 60,   # 60 requisições de API por minuto
            'default': 100  # 100 requisições gerais por minuto
        }
    
    def __call__(self, request):
        if self.is_rate_limited(request):
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'error': 'Muitas requisições. Tente novamente em alguns minutos.',
                    'retry_after': 60
                }, status=429)
            else:
                return HttpResponseForbidden("Muitas requisições. Tente novamente em alguns minutos.")
        
        response = self.get_response(request)
        return response
    
    def is_rate_limited(self, request):
        """
        Verifica se a requisição deve ser limitada
        """
        ip_address = self.get_client_ip(request)
        
        # Determinar tipo de requisição
        rate_type = self.get_rate_type(request)
        limit = self.rate_limits.get(rate_type, self.rate_limits['default'])
        
        cache_key = f'rate_limit_{rate_type}_{ip_address}'
        
        # Contar requisições na janela atual (1 minuto)
        current_requests = cache.get(cache_key, 0)
        
        if current_requests >= limit:
            return True
        
        # Incrementar contador
        cache.set(cache_key, current_requests + 1, 60)  # 60 segundos
        return False
    
    def get_rate_type(self, request):
        """
        Determina o tipo de taxa baseado na URL
        """
        path = request.path.lower()
        
        if '/login' in path:
            return 'login'
        elif '/importar' in path:
            return 'import'
        elif path.startswith('/api/'):
            return 'api'
        else:
            return 'default'
    
    def get_client_ip(self, request):
        """
        Obtém o IP real do cliente
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class AuditMiddleware:
    """
    Middleware para auditoria automática de ações
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Ações que devem ser auditadas
        self.audit_paths = [
            '/admin-panel/',
            '/admin/',
            '/teacher-portal/turma/',
        ]
        
        self.sensitive_actions = [
            'POST',   # Criação/Atualização
            'DELETE', # Exclusão
        ]
    
    def __call__(self, request):
        start_time = time.time()
        
        response = self.get_response(request)
        
        # Auditar se necessário
        if self.should_audit(request):
            self.log_action(request, response, start_time)
        
        return response
    
    def should_audit(self, request):
        """
        Determina se a ação deve ser auditada
        """
        # Auditar ações sensíveis
        if request.method in self.sensitive_actions:
            return True
        
        # Auditar acessos a paths específicos
        for path in self.audit_paths:
            if request.path.startswith(path):
                return True
        
        return False
    
    def log_action(self, request, response, start_time):
        """
        Registra a ação no log de auditoria
        """
        try:
            from core.audit import Logger
            
            processing_time = time.time() - start_time
            
            description = f"{request.method} {request.path}"
            if request.user.is_authenticated:
                description = f"[{request.user.username}] {description}"
            
            details = {
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'processing_time': round(processing_time, 3),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200]
            }
            
            # Determinar severidade baseada no status code
            if response.status_code >= 500:
                severity = 'HIGH'
            elif response.status_code >= 400:
                severity = 'MEDIUM'
            else:
                severity = 'LOW'
            
            Logger.log_action(
                user=request.user if request.user.is_authenticated else None,
                action='VIEW' if request.method == 'GET' else request.method,
                description=description,
                severity=severity,
                details=details,
                request=request
            )
            
        except Exception as e:
            logger.error(f"Erro ao registrar auditoria: {e}")