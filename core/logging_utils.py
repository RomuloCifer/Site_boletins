"""
Sistema de Logs Simplificado para o Sistema de Notas
"""

import logging
from datetime import datetime
from django.contrib.auth.models import User
from django.utils import timezone

logger = logging.getLogger(__name__)

class SimpleLogger:
    """
    Sistema de logs simplificado
    """
    
    @staticmethod
    def log_action(user, action, description, severity='LOW', request=None):
        """
        Registra uma ação no sistema de forma simples
        """
        try:
            from core.models import AuditLog
            
            log_data = {
                'usuario': user if user and user.is_authenticated else None,
                'acao': action,
                'severidade': severity,
                'descricao': description,
            }
            
            if request:
                log_data.update({
                    'ip_address': SimpleLogger._get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500]
                })
            
            AuditLog.objects.create(**log_data)
            
            # Log também no sistema padrão do Django
            log_message = f"{action} - {description}"
            if user and user.is_authenticated:
                log_message = f"[{user.username}] {log_message}"
            
            if severity == 'CRITICAL':
                logger.critical(log_message)
            elif severity == 'HIGH':
                logger.error(log_message)
            elif severity == 'MEDIUM':
                logger.warning(log_message)
            else:
                logger.info(log_message)
                
        except Exception as e:
            # Fallback para log básico se houver erro
            logger.error(f"Erro ao criar log de auditoria: {e}")
    
    @staticmethod
    def log_login(user, success=True, ip_address=None, user_agent=None, request=None):
        """
        Registra tentativa de login
        """
        description = f"Login {'bem-sucedido' if success else 'falhado'} para {user.username if user else 'usuário desconhecido'}"
        severity = 'LOW' if success else 'MEDIUM'
        
        # Se não tiver request mas tiver IP e user agent, criar um objeto mock
        if not request and (ip_address or user_agent):
            class MockRequest:
                def __init__(self, ip, ua):
                    self.META = {'HTTP_USER_AGENT': ua or ''}
                    self._ip = ip
                    
                def get_client_ip(self):
                    return self._ip
                    
            mock_request = MockRequest(ip_address, user_agent)
            
            # Usar o MockRequest apenas se tivermos dados para ele
            request = mock_request
        
        SimpleLogger.log_action(
            user=user if success else None,
            action='LOGIN',
            description=description,
            severity=severity,
            request=request
        )
    
    @staticmethod
    def log_import(user, file_name, success_count, error_count, request=None):
        """
        Registra importação de dados
        """
        severity = 'LOW' if error_count == 0 else 'MEDIUM'
        description = f"Importação de {file_name}: {success_count} sucessos, {error_count} erros"
        
        SimpleLogger.log_action(
            user=user,
            action='IMPORT',
            description=description,
            severity=severity,
            request=request
        )
    
    @staticmethod
    def log_error(user, error_message, request=None):
        """
        Registra erro do sistema
        """
        SimpleLogger.log_action(
            user=user,
            action='ERROR',
            description=f"Erro do sistema: {error_message}",
            severity='HIGH',
            request=request
        )
    
    @staticmethod
    def _get_client_ip(request):
        """
        Obtém o IP real do cliente
        """
        # Se for um MockRequest, usar o método personalizado
        if hasattr(request, 'get_client_ip'):
            return request.get_client_ip()
            
        # Para requests normais do Django
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip