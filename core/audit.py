# Sistema de Logs Personalizado para o Sistema de Notas
import logging
import json
from datetime import datetime
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models

class AuditLog(models.Model):
    """
    Modelo para logs de auditoria do sistema
    """
    ACAO_CHOICES = [
        ('CREATE', 'Criação'),
        ('UPDATE', 'Atualização'),
        ('DELETE', 'Exclusão'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('IMPORT', 'Importação'),
        ('EXPORT', 'Exportação'),
        ('VIEW', 'Visualização'),
        ('ERROR', 'Erro'),
    ]
    
    SEVERIDADE_CHOICES = [
        ('LOW', 'Baixa'),
        ('MEDIUM', 'Média'),
        ('HIGH', 'Alta'),
        ('CRITICAL', 'Crítica'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    acao = models.CharField(max_length=10, choices=ACAO_CHOICES)
    severidade = models.CharField(max_length=10, choices=SEVERIDADE_CHOICES, default='LOW')
    modelo_afetado = models.CharField(max_length=100, blank=True)
    objeto_id = models.PositiveIntegerField(blank=True, null=True)
    descricao = models.TextField()
    detalhes_json = models.JSONField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Log de Auditoria"
        verbose_name_plural = "Logs de Auditoria"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp', 'acao']),
            models.Index(fields=['usuario', 'timestamp']),
            models.Index(fields=['severidade', 'timestamp']),
        ]
    
    def __str__(self):
        acao_display = dict(self.ACAO_CHOICES).get(self.acao, self.acao)
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M')} - {acao_display} - {self.descricao[:50]}"

class SystemMetrics(models.Model):
    """
    Métricas do sistema para monitoramento
    """
    METRIC_CHOICES = [
        ('USERS_ONLINE', 'Usuários Online'),
        ('TOTAL_LOGINS', 'Total de Logins'),
        ('IMPORT_SUCCESS', 'Importações Bem-sucedidas'),
        ('IMPORT_ERRORS', 'Erros de Importação'),
        ('NOTES_CREATED', 'Notas Criadas'),
        ('SYSTEM_ERRORS', 'Erros do Sistema'),
        ('DATABASE_SIZE', 'Tamanho do Banco'),
        ('RESPONSE_TIME', 'Tempo de Resposta'),
    ]
    
    metric_name = models.CharField(max_length=20, choices=METRIC_CHOICES)
    metric_value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    additional_data = models.JSONField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Métrica do Sistema"
        verbose_name_plural = "Métricas do Sistema"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['metric_name', 'timestamp']),
        ]

class Logger:
    """
    Sistema de logs customizado
    """
    
    @staticmethod
    def log_action(user, action, description, model_name=None, object_id=None, 
                   severity='LOW', details=None, request=None):
        """
        Registra uma ação no sistema
        """
        try:
            log_data = {
                'usuario': user if user and user.is_authenticated else None,
                'acao': action,
                'severidade': severity,
                'modelo_afetado': model_name,
                'objeto_id': object_id,
                'descricao': description,
                'detalhes_json': details,
            }
            
            if request:
                log_data.update({
                    'ip_address': Logger._get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500]
                })
            
            AuditLog.objects.create(**log_data)
            
            # Log também no sistema de logs do Django
            logger = logging.getLogger('audit')
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
            logging.error(f"Erro ao criar log de auditoria: {e}")
    
    @staticmethod
    def log_login(user, request, success=True):
        """
        Registra tentativa de login
        """
        description = f"Login {'bem-sucedido' if success else 'falhado'} para {user.username if user else 'usuário desconhecido'}"
        severity = 'LOW' if success else 'MEDIUM'
        
        Logger.log_action(
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
        details = {
            'file_name': file_name,
            'success_count': success_count,
            'error_count': error_count,
            'timestamp': timezone.now().isoformat()
        }
        
        severity = 'LOW' if error_count == 0 else 'MEDIUM'
        description = f"Importação de {file_name}: {success_count} sucessos, {error_count} erros"
        
        Logger.log_action(
            user=user,
            action='IMPORT',
            description=description,
            severity=severity,
            details=details,
            request=request
        )
    
    @staticmethod
    def log_error(user, error_message, error_type=None, request=None):
        """
        Registra erro do sistema
        """
        details = {
            'error_type': error_type,
            'error_message': str(error_message),
            'timestamp': timezone.now().isoformat()
        }
        
        Logger.log_action(
            user=user,
            action='ERROR',
            description=f"Erro do sistema: {error_message}",
            severity='HIGH',
            details=details,
            request=request
        )
    
    @staticmethod
    def _get_client_ip(request):
        """
        Obtém o IP real do cliente
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class PerformanceMonitor:
    """
    Monitor de performance do sistema
    """
    
    @staticmethod
    def record_metric(metric_name, value, additional_data=None):
        """
        Registra uma métrica do sistema
        """
        try:
            SystemMetrics.objects.create(
                metric_name=metric_name,
                metric_value=value,
                additional_data=additional_data
            )
        except Exception as e:
            logging.error(f"Erro ao registrar métrica {metric_name}: {e}")
    
    @staticmethod
    def get_metrics_summary(metric_name, hours=24):
        """
        Obtém resumo de métricas das últimas horas
        """
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_time = timezone.now() - timedelta(hours=hours)
        
        metrics = SystemMetrics.objects.filter(
            metric_name=metric_name,
            timestamp__gte=cutoff_time
        ).order_by('timestamp')
        
        if not metrics.exists():
            return None
        
        values = [m.metric_value for m in metrics]
        
        return {
            'count': len(values),
            'average': sum(values) / len(values),
            'min': min(values),
            'max': max(values),
            'latest': values[-1],
            'trend': 'up' if len(values) > 1 and values[-1] > values[0] else 'down'
        }