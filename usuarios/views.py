from django.shortcuts import render
from rest_framework import viewsets
from .models import Especialista, Paciente
from .serializers import EspecialistaSerializer, PacienteSerializer

# Create your views here.

class EspecialistaViewSet(viewsets.ModelViewSet):
    queryset = Especialista.objects.all()
    serializer_class = EspecialistaSerializer

class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
