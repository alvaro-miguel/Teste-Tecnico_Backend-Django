from rest_framework import permissions

class IsEspecialistaOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and getattr(request.user, 'tipo_usuario', None) == 'ESPECIALISTA'

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'especialista'):
            return obj.especialista.usuario == request.user
        elif hasattr(obj, 'agenda'):
            return obj.agenda.especialista.usuario == request.user
        return False

class IsPacienteOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and getattr(request.user, 'tipo_usuario', None) == 'PACIENTE'

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'paciente'):
            return obj.paciente.usuario == request.user
        return False


class IsInterno(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and (getattr(request.user, 'tipo_usuario', None) == 'INTERNO' or request.user.is_superuser)

