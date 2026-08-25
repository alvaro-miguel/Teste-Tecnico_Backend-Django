from rest_framework import serializers
from .models import Especialista, Paciente
from agendamentos.serializers import EspecialidadeSerializer

class PacienteSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='usuario.first_name', read_only=True)
    telefone = serializers.CharField(source='usuario.telefone', read_only=True)
    
    class Meta:
        model = Paciente
        fields = ['id', 'nome', 'telefone', 'ativo', 'criado_em', 'atualizado_em']


class EspecialistaSerializer(serializers.ModelSerializer):
    especialidade_detalhe = EspecialidadeSerializer(source='especialidade', read_only=True)
    nome = serializers.CharField(source='usuario.first_name', read_only=True)
    
    class Meta:
        model = Especialista
        fields = ['id', 'nome', 'crm', 'especialidade', 'especialidade_detalhe', 'ativo', 'criado_em', 'atualizado_em']
