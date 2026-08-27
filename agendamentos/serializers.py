from rest_framework import serializers
from .models import Especialidade, Agenda, HorarioGerado, Consulta
from usuarios.models import Usuario, Especialista, Paciente

class EspecialidadeSerializer(serializers.ModelSerializer):
    class Meta:     
        model = Especialidade
        fields = ['id', 'nome_especialidade', 'ativo', 'criado_em', 'atualizado_em']

        
class HorarioGeradoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HorarioGerado
        fields = ['id', 'horario_inicio', 'horario_fim', 'status', 'data', 'criado_em', 'atualizado_em']


class AgendaSerializer(serializers.ModelSerializer):
    horarios = HorarioGeradoSerializer(many=True, read_only=True)
    nome_especialista = serializers.CharField(source='especialista.usuario.first_name', read_only=True)

    class Meta:
        model = Agenda
        fields = [
            'id', 'especialista', 'nome_especialista', 'dias_semana', 
            'hora_inicio_expediente', 'hora_fim_expediente', 
            'quantidade_vagas_dia', 'horarios', 'ativo', 'criado_em', 'atualizado_em'
        ]
        read_only_fields = ['especialista']

    def validate(self, data):
        hora_inicio = data.get('hora_inicio_expediente')
        hora_fim = data.get('hora_fim_expediente')

        if hora_inicio and hora_fim and hora_inicio >= hora_fim:
            raise serializers.ValidationError(
                {"hora_inicio_expediente": "A hora de início deve ser menor que a hora de término."}
            )
        return data


class ConsultaSerializer(serializers.ModelSerializer):
    nome_paciente = serializers.CharField(source='paciente.usuario.first_name', read_only=True)
    data_hora = serializers.SerializerMethodField()

    class Meta:
        model = Consulta
        fields = ['id', 'paciente', 'nome_paciente', 'horario_gerado', 'data_hora', 'ativo', 'criado_em', 'atualizado_em']
        read_only_fields = ['paciente']

    def get_data_hora(self, obj):
        return f"{obj.horario_gerado.data} ({obj.horario_gerado.agenda.get_dias_semana_display()}) às {obj.horario_gerado.horario_inicio}"
