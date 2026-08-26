from rest_framework import permissions

class IsEspecialistaOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.tipo_usuario == 'ESPECIALISTA'

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'especialista'):
            return obj.especialista.usuario == request.user
        elif hasattr(obj, 'agenda'):
            return obj.agenda.especialista.usuario == request.user
        return False


class IsPacienteOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.tipo_usuario == 'PACIENTE'

    def has_object_permission(self, request, view, obj):
        # Garante que a consulta pertence ao paciente logado
        return obj.paciente.usuario == request.user