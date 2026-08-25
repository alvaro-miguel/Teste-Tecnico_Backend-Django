from rest_framework import serializers
from .models import Usuario, Especialidade, Especialista, Paciente, Agenda, HorarioGerado, Consulta

class EspecialidadeSerializer(serializers.ModelSerializer):
    class Meta:     
        model = Especialidade
        fields = ['id', 'nome_especialidade', 'ativo', 'criado_em', 'editado_em']


class EspecialistaSerializer(serializers.ModelSerializer):
    especialidade_detalhe = EspecialidadeSerializer(source='especialidade', read_only=True)
    nome = serializers.CharField(source='usuario.first_name', read_only=True)
    
    class Meta:
        model = Especialista
        fields = ['id', 'nome', 'crm', 'especialidade', 'especialidade_detalhe', 'ativo', 'criado_em', 'editado_em']


class PacienteSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='usuario.first_name', read_only=True)
    telefone = serializers.CharField(source='usuario.telefone', read_only=True)
    
    class Meta:
        model = Paciente
        fields = ['id', 'nome', 'telefone', 'ativo', 'criado_em', 'editado_em']


class HorarioGeradoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HorarioGerado
        fields = ['id', 'horario_inicio', 'horario_fim', 'status', 'data', 'criado_em', 'editado_em']


class AgendaSerializer(serializers.ModelSerializer):
    horarios = HorarioGeradoSerializer(many=True, read_only=True)
    nome_especialista = serializers.CharField(source='especialista.usuario.first_name', read_only=True)

    class Meta:
        model = Agenda
        fields = [
            'id', 'especialista', 'nome_especialista', 'dias_semana', 
            'hora_inicio_expediente', 'hora_fim_expediente', 
            'quantidade_vagas_dia', 'horarios', 'ativo', 'criado_em', 'editado_em'
        ]


class ConsultaSerializer(serializers.ModelSerializer):
    nome_paciente = serializers.CharField(source='paciente.usuario.first_name', read_only=True)
    data_hora = serializers.SerializerMethodField()

    class Meta:
        model = Consulta
        fields = ['id', 'paciente', 'nome_paciente', 'horario_gerado', 'data_hora', 'ativo', 'criado_em', 'editado_em']

    def get_data_hora(self, obj):
        return f"{obj.horario_gerado.data} ({obj.horario_gerado.agenda.get_dias_semana_display()}) às {obj.horario_gerado.horario_inicio}"