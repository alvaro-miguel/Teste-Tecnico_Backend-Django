from django.shortcuts import render
from rest_framework import viewsets
from .models import Especialista, Paciente
from .serializers import EspecialistaSerializer, PacienteSerializer
from agendamentos.permissions import IsInterno

# Create your views here.

class EspecialistaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsInterno]
    queryset = Especialista.objects.all()
    serializer_class = EspecialistaSerializer

class PacienteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsInterno]
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
