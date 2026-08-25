from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from core.models import CommonModel

# Create your models here.

class TipoUsuario(models.TextChoices):
    ESPECIALISTA = 'ESPECIALISTA', 'Especialista'
    PACIENTE = 'PACIENTE', 'Paciente'
    INTERNO = 'INTERNO', 'Interno'


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


class Usuario(AbstractUser):

    tipo_usuario = models.CharField(
        max_length=15,
        choices=TipoUsuario.choices,
        null=True,
        blank=True
    )
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} - {self.tipo_usuario}"


class Especialidade(CommonModel):
    nome_especialidade = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome_especialidade


class Especialista(CommonModel):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='especialista_perfil')
    especialidade = models.ForeignKey(Especialidade, on_delete=models.PROTECT, related_name='especialistas')
    crm = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"Dr(a). {self.usuario.first_name} - CRM: {self.crm}"


class Paciente(CommonModel):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='paciente_perfil')

    def __str__(self):
        return self.usuario.first_name or self.usuario.username


class Agenda(CommonModel):

    especialista = models.ForeignKey(Especialista, on_delete=models.CASCADE, related_name='agendas')
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
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='consultas')
    horario_gerado = models.OneToOneField(HorarioGerado, on_delete=models.CASCADE, related_name='consulta')

    def __str__(self):
        return f"Consulta de {self.paciente} às {self.horario_gerado.horario_inicio}"
