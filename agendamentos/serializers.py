from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Especialidade, Agenda, HorarioGerado, Consulta

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
        valores = {
            'especialista': getattr(self.instance, 'especialista', None),
            'dias_semana': getattr(self.instance, 'dias_semana', None),
            'hora_inicio_expediente': getattr(
                self.instance, 'hora_inicio_expediente', None
            ),
            'hora_fim_expediente': getattr(
                self.instance, 'hora_fim_expediente', None
            ),
            'quantidade_vagas_dia': getattr(
                self.instance, 'quantidade_vagas_dia', None
            ),
        }
        valores.update(data)

        try:
            Agenda(**valores).clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict) from exc

        return data


class ConsultaSerializer(serializers.ModelSerializer):
    nome_paciente = serializers.CharField(source='paciente.usuario.first_name', read_only=True)
    data_hora = serializers.SerializerMethodField()

    class Meta:
        model = Consulta
        fields = ['id', 'paciente', 'nome_paciente', 'horario_gerado', 'data_hora', 'ativo', 'criado_em', 'atualizado_em']
        read_only_fields = ['paciente']

    def get_data_hora(self, obj) -> str:
        return f"{obj.horario_gerado.data} ({obj.horario_gerado.agenda.get_dias_semana_display()}) às {obj.horario_gerado.horario_inicio}"
