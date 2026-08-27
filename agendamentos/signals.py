from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Agenda
from .services import gerar_horarios


@receiver(post_save, sender=Agenda)
def gerar_horarios_apos_criar_agenda(sender, instance, created, **kwargs):
    if created:
        gerar_horarios(instance)