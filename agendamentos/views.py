from rest_framework import viewsets
from .models import Especialidade, Agenda, HorarioGerado, Consulta
from .serializers import (
    EspecialidadeSerializer, 
    AgendaSerializer, 
    HorarioGeradoSerializer, 
    ConsultaSerializer
)
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from .services import agendar_consulta
from .permissions import (
    ConsultaPermission,
    IsEspecialistaOwner,
    IsInternoOrReadOnly,
    is_usuario_interno,
)
from django_filters.rest_framework import DjangoFilterBackend

class EspecialidadeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsInternoOrReadOnly]
    queryset = Especialidade.objects.all()
    serializer_class = EspecialidadeSerializer


class AgendaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsEspecialistaOwner]
    queryset = Agenda.objects.all()
    serializer_class = AgendaSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and getattr(user, 'tipo_usuario', None) == 'ESPECIALISTA':
            return Agenda.objects.filter(especialista__usuario=user)
        return Agenda.objects.none()

    def perform_create(self, serializer):
        try:
            especialista = self.request.user.especialista_perfil
        except ObjectDoesNotExist as exc:
            raise ValidationError({
                'especialista': 'O usuário autenticado não possui perfil de especialista.'
            }) from exc

        serializer.save(especialista=especialista)
        

class HorarioGeradoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HorarioGerado.objects.all()
    serializer_class = HorarioGeradoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'data', 'agenda__especialista']


class ConsultaViewSet(viewsets.ModelViewSet):
    permission_classes = [ConsultaPermission]
    queryset = Consulta.objects.all()
    serializer_class = ConsultaSerializer

    def get_queryset(self):
        user = self.request.user
        if is_usuario_interno(user):
            return Consulta.objects.all()
        if getattr(user, 'tipo_usuario', None) == 'PACIENTE':
            return Consulta.objects.filter(paciente__usuario=user)
        if getattr(user, 'tipo_usuario', None) == 'ESPECIALISTA':
            return Consulta.objects.filter(
                horario_gerado__agenda__especialista__usuario=user
            )
        return Consulta.objects.none()

    def perform_create(self, serializer):
        try:
            paciente = self.request.user.paciente_perfil
        except ObjectDoesNotExist as exc:
            raise ValidationError({
                'paciente': 'O usuário autenticado não possui perfil de paciente.'
            }) from exc

        horario = serializer.validated_data.get('horario_gerado')
        
        consulta = agendar_consulta(paciente.id, horario.id)
        serializer.instance = consulta
