from django.db import models
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

    def clean(self):
        if self.hora_inicio_expediente and self.hora_fim_expediente:
            if self.hora_inicio_expediente >= self.hora_fim_expediente:
                raise ValidationError("Hora de início do expediente deve ser anterior a hora do fim expediente")


    def __str__(self):
        return f"Agenda: {self.especialista} - {self.get_dias_semana_display()}"


class HorarioGerado(CommonModel):

    agenda = models.ForeignKey(Agenda, on_delete=models.CASCADE, related_name='horarios')
    data = models.DateField()
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()
    status = models.CharField(
        max_length=15,
        choices=StatusHorario.choices,
        default=StatusHorario.DISPONIVEL
    )

    def __str__(self):
        return f"{self.agenda.especialista} | {self.horario_inicio}/{self.horario_fim} - {self.status}"


class Consulta(CommonModel):
    paciente = models.ForeignKey('usuarios.Paciente', on_delete=models.CASCADE, related_name='consultas')
    horario_gerado = models.OneToOneField(HorarioGerado, on_delete=models.CASCADE, related_name='consulta')

    def __str__(self):
        return f"Consulta de {self.paciente} às {self.horario_gerado.horario_inicio}"
