from functools import wraps
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages

def group_required(*group_names):
    """
    Decorator que verifica se o usuário pertence a pelo menos um dos grupos especificados.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('teacher_portal:login')
            
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if not request.user.is_staff:
                messages.error(request, "Você não tem permissão para acessar esta área.")
                return redirect('teacher_portal:dashboard')
            
            user_groups = request.user.groups.values_list('name', flat=True)
            if not any(group in user_groups for group in group_names):
                messages.error(request, f"Você precisa pertencer a um dos grupos: {', '.join(group_names)}")
                return redirect('teacher_portal:dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def permission_required_custom(permission_name):
    """
    Decorator que verifica permissão específica.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('teacher_portal:login')
            
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if not request.user.has_perm(permission_name):
                messages.error(request, f"Você não tem a permissão '{permission_name}' necessária.")
                return redirect('teacher_portal:dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# Decorators específicos para diferentes níveis de acesso
def admin_only(view_func):
    """Apenas superusuários ou grupo 'Administradores'"""
    return group_required('Administradores')(view_func)

def coordinador_or_admin(view_func):
    """Coordenadores ou Administradores"""
    return group_required('Coordenadores', 'Administradores')(view_func)

def secretaria_or_above(view_func):
    """Secretaria, Coordenadores ou Administradores"""
    return group_required('Secretaria', 'Coordenadores', 'Administradores')(view_func)