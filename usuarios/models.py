from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import CommonModel

# Create your models here.


class TipoUsuario(models.TextChoices):
    ESPECIALISTA = 'ESPECIALISTA', 'Especialista'
    PACIENTE = 'PACIENTE', 'Paciente'
    INTERNO = 'INTERNO', 'Interno'


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


class Especialista(CommonModel):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='especialista_perfil')
    especialidade = models.ForeignKey('agendamentos.Especialidade', on_delete=models.PROTECT, related_name='especialistas')
    crm = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"Dr(a). {self.usuario.first_name} - CRM: {self.crm}"


class Paciente(CommonModel):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='paciente_perfil')

    def __str__(self):
        return self.usuario.first_name or self.usuario.username

