from django.contrib import admin
from .models import Usuario, Especialidade, Especialista, Paciente, Agenda, HorarioGerado, Consulta

# Register your models here.

admin.site.register(Especialidade)
admin.site.register(Agenda)
admin.site.register(HorarioGerado)
admin.site.register(Consulta)