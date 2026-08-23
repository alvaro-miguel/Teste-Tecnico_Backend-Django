from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

# Create your models here.

class BaseModel(models.Model):
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        self.ativo = False
        self.save()


class Usuario(AbstractUser):
    TIPO_USUARIO_CHOICES = (
        ('ESPECIALISTA','Especialista'),
        ('PACIENTE', 'Paciente'),
        ('INTERNO', 'Equipe interna')
    )

    tipo_usuario = models.CharField(max_length=15, choices=TIPO_USUARIO_CHOICES, null=True, blank=True)
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} - {self.tipo_usuario}"


class Especialidade(BaseModel):
    nome_especialidade = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome_especialidade


class Especialista(BaseModel):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='especialista_perfil')
    especialidade = models.ForeignKey(Especialidade, on_delete=models.PROTECT, related_name='especialistas')
    crm = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"Dr(a). {self.usuario.first_name} - CRM: {self.crm}"


class Paciente(BaseModel):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='paciente_perfil')

    def __str__(self):
        return self.usuario.first_name or self.usuario.username


class Agenda(BaseModel):
    DIAS_SEMANA_CHOICE = (
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    )

    especialista = models.ForeignKey(Especialista, on_delete=models.CASCADE, related_name='agendas')
    dias_semana = models.IntegerField(choices=DIAS_SEMANA_CHOICE)
    hora_inicio_expediente = models.TimeField()
    hora_fim_expediente = models.TimeField()
    quantidade_vagas_dia = models.IntegerField(validators=[MinValueValidator(1)])

    def clean(self):
        if self.hora_inicio_expediente and self.hora_fim_expediente:
            if self.hora_inicio_expediente >= self.hora_fim_expediente:
                raise ValidationError("Hora de início do expediente deve ser anterior a hora do fim expediente")


    def __str__(self):
        return f"Agenda: {self.especialista} - {self.get_dias_semana_display()}"


class HorarioGerado(BaseModel):
    STATUS_CHOICE = (
        ('DISPONIVEL', 'Disponível'),
        ('RESERVADO', 'Reservado')
    )

    agenda = models.ForeignKey(Agenda, on_delete=models.CASCADE, related_name='horarios')
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICE, default='DISPONIVEL')

    def __str__(self):
        return f"{self.agenda.especialista} | {self.horario_inicio}/{self.horario_fim} - {self.status}"


class Consulta(BaseModel):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='consultas')
    horario_gerado = models.OneToOneField(HorarioGerado, on_delete=models.CASCADE, related_name='consulta')

    def clean(self):
        if self.horario_gerado.status != 'DISPONIVEL':
            raise ValidationError("Este horário não está disponível, por favor escolha outro")

    def save(self, *args, **kwargs):
        if not self.pk:
            self.horario_gerado.status = 'RESERVADO'
            self.horario_gerado.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Consulta de {self.paciente} às {self.horario_gerado.horario_inicio}"
    
