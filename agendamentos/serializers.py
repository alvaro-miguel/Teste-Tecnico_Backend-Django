from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Especialidade, Agenda, HorarioGerado, Consulta
from .services import atualizar_agenda, criar_agenda

class EspecialidadeSerializer(serializers.ModelSerializer):
    class Meta:     
        model = Especialidade
        fields = ['id', 'nome_especialidade', 'ativo', 'criado_em', 'atualizado_em']
        extra_kwargs = {
            'nome_especialidade': {'validators': []},
        }

    def validate_nome_especialidade(self, value):
        nome = ' '.join(value.split())
        if not nome:
            raise serializers.ValidationError(
                'Este campo não pode ficar em branco.'
            )
        especialidade_id = self.instance.id if self.instance else None
        if Especialidade.all_objects.filter(
            nome_especialidade__iexact=nome
        ).exclude(id=especialidade_id).exists():
            raise serializers.ValidationError(
                'Já existe uma especialidade com este nome.'
            )
        return nome

        
class HorarioGeradoSerializer(serializers.ModelSerializer):
    agenda = serializers.IntegerField(source='agenda_id', read_only=True)
    especialista = serializers.IntegerField(
        source='agenda.especialista_id',
        read_only=True,
    )
    nome_especialista = serializers.CharField(
        source='agenda.especialista.usuario.first_name',
        read_only=True,
    )
    especialidade = serializers.CharField(
        source='agenda.especialista.especialidade.nome_especialidade',
        read_only=True,
    )

    class Meta:
        model = HorarioGerado
        fields = [
            'id',
            'agenda',
            'especialista',
            'nome_especialista',
            'especialidade',
            'horario_inicio',
            'horario_fim',
            'status',
            'data',
            'criado_em',
            'atualizado_em',
        ]


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
        read_only_fields = [
            'especialista',
            'ativo',
            'criado_em',
            'atualizado_em',
        ]

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

        agenda = Agenda(**valores)
        if self.instance:
            agenda.pk = self.instance.pk

        try:
            agenda.clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict) from exc

        return data

    def create(self, validated_data):
        return criar_agenda(**validated_data)

    def update(self, instance, validated_data):
        return atualizar_agenda(instance, validated_data)


class ConsultaSerializer(serializers.ModelSerializer):
    nome_paciente = serializers.CharField(source='paciente.usuario.first_name', read_only=True)
    nome_especialista = serializers.CharField(
        source='horario_gerado.agenda.especialista.usuario.first_name',
        read_only=True,
    )
    especialidade = serializers.CharField(
        source='horario_gerado.agenda.especialista.especialidade.nome_especialidade',
        read_only=True,
    )
    data_hora = serializers.SerializerMethodField()

    class Meta:
        model = Consulta
        fields = [
            'id',
            'paciente',
            'nome_paciente',
            'horario_gerado',
            'nome_especialista',
            'especialidade',
            'data_hora',
            'ativo',
            'criado_em',
            'atualizado_em',
        ]
        read_only_fields = [
            'paciente',
            'ativo',
            'criado_em',
            'atualizado_em',
        ]

    def get_data_hora(self, obj) -> str:
        return f"{obj.horario_gerado.data} ({obj.horario_gerado.agenda.get_dias_semana_display()}) às {obj.horario_gerado.horario_inicio}"
