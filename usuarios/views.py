from rest_framework import viewsets
from .models import Especialista, Paciente
from .serializers import EspecialistaSerializer, PacienteSerializer
from agendamentos.permissions import IsInterno, IsInternoOrReadOnly

class EspecialistaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsInternoOrReadOnly]
    queryset = Especialista.objects.all()
    serializer_class = EspecialistaSerializer

class PacienteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsInterno]
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
