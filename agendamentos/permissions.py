from rest_framework import permissions


def is_usuario_interno(user):
    return bool(
        user
        and user.is_authenticated
        and (
            getattr(user, 'tipo_usuario', None) == 'INTERNO'
            or user.is_superuser
        )
    )


class IsInterno(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_usuario_interno(request.user)


class IsInternoOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return is_usuario_interno(request.user)


class IsEspecialistaOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'tipo_usuario', None) == 'ESPECIALISTA'
        )

    def has_object_permission(self, request, view, obj):
        return obj.especialista.usuario_id == request.user.id


class ConsultaPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if view.action == 'create':
            return getattr(user, 'tipo_usuario', None) == 'PACIENTE'

        if view.action not in {'list', 'retrieve'}:
            return False

        return bool(
            getattr(user, 'tipo_usuario', None)
            in {'PACIENTE', 'ESPECIALISTA', 'INTERNO'}
            or user.is_superuser
        )

    def has_object_permission(self, request, view, obj):
        user = request.user
        if is_usuario_interno(user):
            return True
        if getattr(user, 'tipo_usuario', None) == 'PACIENTE':
            return obj.paciente.usuario_id == user.id
        if getattr(user, 'tipo_usuario', None) == 'ESPECIALISTA':
            return obj.horario_gerado.agenda.especialista.usuario_id == user.id
        return False
