from rest_framework import viewsets
from .models import Especialidade, Agenda, HorarioGerado, Consulta
from .serializers import (
    EspecialidadeSerializer, 
    AgendaSerializer, 
    HorarioGeradoSerializer, 
    ConsultaSerializer
)
from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from .services import agendar_consulta, gerar_horarios
from .permissions import IsEspecialistaOwner, IsPacienteOwner, IsInterno
from django_filters.rest_framework import DjangoFilterBackend

class EspecialidadeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsInterno]
    queryset = Especialidade.objects.all()
    serializer_class = EspecialidadeSerializer


class AgendaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsEspecialistaOwner]
    serializer_class = AgendaSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and getattr(user, 'tipo_usuario', None) == 'ESPECIALISTA':
            return Agenda.objects.filter(especialista__usuario=user)
        return Agenda.objects.none()

    def perform_create(self, serializer):
        agenda = serializer.save()
        gerar_horarios(agenda)


class HorarioGeradoViewSet(viewsets.ModelViewSet):
    queryset = HorarioGerado.objects.all()
    serializer_class = HorarioGeradoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'data', 'agenda__especialista']


class ConsultaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsPacienteOwner]
    serializer_class = ConsultaSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if getattr(user, 'tipo_usuario', None) == 'PACIENTE':
                return Consulta.objects.filter(paciente__usuario=user)
            elif getattr(user, 'tipo_usuario', None) == 'ESPECIALISTA':
                return Consulta.objects.filter(horario_gerado__agenda__especialista__usuario=user)
        return Consulta.objects.none()

    def perform_create(self, serializer):
        paciente = serializer.validated_data.get('paciente')
        horario = serializer.validated_data.get('horario_gerado')
        
        consulta = agendar_consulta(paciente.id, horario.id)
        serializer.instance = consulta