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
from rest_framework.permissions import IsAuthenticated
from .permissions import IsEspecialistaOwner, IsPacienteOwner
from django_filters.rest_framework import DjangoFilterBackend

class EspecialidadeViewSet(viewsets.ModelViewSet):
    queryset = Especialidade.objects.all()
    serializer_class = EspecialidadeSerializer


class AgendaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsEspecialistaOwner]
    queryset = Agenda.objects.all()
    serializer_class = AgendaSerializer

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
    queryset = Consulta.objects.all()
    serializer_class = ConsultaSerializer

    def create(self, request, *args, **kwargs):
        paciente_id = request.data.get('paciente')
        horario_id = request.data.get('horario_gerado')

        try:
            consulta = agendar_consulta(paciente_id, horario_id)
            serializer = self.get_serializer(consulta)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"erro": str(e)},
                            status=status.HTTP_400_BAD_REQUEST)