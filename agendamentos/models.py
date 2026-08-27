from datetime import datetime

from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Lower
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from core.models import CommonModel

# Create your models here.

class DiasDaSemana(models.IntegerChoices):
    SEGUNDA = 0, 'Segunda-feira'
    TERCA = 1, 'Terça-feira'
    QUARTA = 2, 'Quarta-feira'
    QUINTA = 3, 'Quinta-feira'
    SEXTA = 4, 'Sexta-feira'
    SABADO = 5, 'Sábado'
    DOMINGO = 6, 'Domingo'


class StatusHorario(models.TextChoices):
    DISPONIVEL = 'DISPONIVEL', 'Disponível'
    RESERVADO = 'RESERVADO', 'Reservado'


class Especialidade(CommonModel):
    nome_especialidade = models.CharField(max_length=100, unique=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('nome_especialidade'),
                name='especialidade_nome_unico_case_insensitive',
            ),
        ]

    def __str__(self):
        return self.nome_especialidade

    
class Agenda(CommonModel):

    especialista = models.ForeignKey('usuarios.Especialista', on_delete=models.CASCADE, related_name='agendas')
    dias_semana = models.IntegerField(
        choices=DiasDaSemana.choices
    )
    hora_inicio_expediente = models.TimeField()
    hora_fim_expediente = models.TimeField()
    quantidade_vagas_dia = models.IntegerField(validators=[MinValueValidator(1)])

    def delete(self, *args, **kwargs):
        quantidade_horarios, detalhes_horarios = self.horarios.all().delete()
        quantidade_agenda, detalhes_agenda = super().delete(*args, **kwargs)

        detalhes = detalhes_horarios.copy()
        for modelo, total in detalhes_agenda.items():
            detalhes[modelo] = detalhes.get(modelo, 0) + total

        return quantidade_horarios + quantidade_agenda, detalhes

    def clean(self):
        super().clean()

        if not self.hora_inicio_expediente or not self.hora_fim_expediente:
            return

        if self.hora_inicio_expediente >= self.hora_fim_expediente:
            raise ValidationError({
                'hora_fim_expediente': (
                    'A hora de fim do expediente deve ser posterior à hora de início.'
                )
            })

        if self.quantidade_vagas_dia:
            inicio = datetime.combine(datetime.min.date(), self.hora_inicio_expediente)
            fim = datetime.combine(datetime.min.date(), self.hora_fim_expediente)
            duracao_segundos = int((fim - inicio).total_seconds())

            if self.quantidade_vagas_dia > duracao_segundos:
                raise ValidationError({
                    'quantidade_vagas_dia': (
                        'A quantidade de vagas não pode gerar horários com '
                        'duração inferior a um segundo.'
                    )
                })

        if self.ativo and self.especialista_id and self.dias_semana is not None:
            agendas_conflitantes = Agenda.objects.filter(
                especialista_id=self.especialista_id,
                dias_semana=self.dias_semana,
                hora_inicio_expediente__lt=self.hora_fim_expediente,
                hora_fim_expediente__gt=self.hora_inicio_expediente,
            )
            if self.pk:
                agendas_conflitantes = agendas_conflitantes.exclude(pk=self.pk)

            if agendas_conflitantes.exists():
                raise ValidationError({
                    'hora_inicio_expediente': (
                        'O especialista já possui uma agenda nesse intervalo.'
                    )
                })


    def __str__(self):
        return f"Agenda: {self.especialista} - {self.get_dias_semana_display()}"


class HorarioGerado(CommonModel):

    agenda = models.ForeignKey(Agenda, on_delete=models.CASCADE, related_name='horarios')
    data = models.DateField(db_index=True)
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()
    status = models.CharField(
        max_length=15,
        choices=StatusHorario.choices,
        default=StatusHorario.DISPONIVEL,
        db_index=True
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(horario_fim__gt=F('horario_inicio')),
                name='horario_fim_posterior_inicio',
            ),
            models.UniqueConstraint(
                fields=['agenda', 'data', 'horario_inicio'],
                condition=Q(ativo=True),
                name='horario_unico_por_agenda_data_inicio',
            ),
        ]

    def __str__(self):
        return f"{self.agenda.especialista} | {self.horario_inicio}/{self.horario_fim} - {self.status}"


class Consulta(CommonModel):
    paciente = models.ForeignKey('usuarios.Paciente', on_delete=models.CASCADE, related_name='consultas')
    horario_gerado = models.OneToOneField(HorarioGerado, on_delete=models.CASCADE, related_name='consulta')

    def __str__(self):
        return f"Consulta de {self.paciente} às {self.horario_gerado.horario_inicio}"
