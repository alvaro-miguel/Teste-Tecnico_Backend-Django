from rest_framework import viewsets
from .models import Especialidade, Especialista, Paciente, Agenda, HorarioGerado, Consulta
from .serializers import (
    EspecialidadeSerializer, 
    EspecialistaSerializer, 
    PacienteSerializer, 
    AgendaSerializer, 
    HorarioGeradoSerializer, 
    ConsultaSerializer
)
from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from .services import agendar_consulta, gerar_horarios

class EspecialidadeViewSet(viewsets.ModelViewSet):
    queryset = Especialidade.objects.all()
    serializer_class = EspecialidadeSerializer

class EspecialistaViewSet(viewsets.ModelViewSet):
    queryset = Especialista.objects.all()
    serializer_class = EspecialistaSerializer

class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer

class AgendaViewSet(viewsets.ModelViewSet):
    queryset = Agenda.objects.all()
    serializer_class = AgendaSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        agenda_id = response.data['id']
        agenda = Agenda.objects.get(id=agenda_id)

        gerar_horarios(agenda)
        return response

class HorarioGeradoViewSet(viewsets.ModelViewSet):
    queryset = HorarioGerado.objects.all()
    serializer_class = HorarioGeradoSerializer

class ConsultaViewSet(viewsets.ModelViewSet):
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