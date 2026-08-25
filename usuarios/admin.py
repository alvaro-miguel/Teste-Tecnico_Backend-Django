from django.contrib import admin
from .models import Usuario, Especialista, Paciente

# Register your models here.

admin.site.register(Usuario)
admin.site.register(Especialista)
admin.site.register(Paciente)
