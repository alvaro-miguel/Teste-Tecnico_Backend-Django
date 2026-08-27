from django.contrib import admin
from .models import Especialidade, Agenda, HorarioGerado, Consulta


class SomenteLeituraAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Especialidade)


@admin.register(Agenda)
class AgendaAdmin(SomenteLeituraAdmin):
    list_display = (
        'id',
        'especialista',
        'dias_semana',
        'hora_inicio_expediente',
        'hora_fim_expediente',
        'ativo',
    )
    list_filter = ('dias_semana', 'ativo')


@admin.register(HorarioGerado)
class HorarioGeradoAdmin(SomenteLeituraAdmin):
    list_display = (
        'id',
        'agenda',
        'data',
        'horario_inicio',
        'horario_fim',
        'status',
    )
    list_filter = ('status', 'data')


@admin.register(Consulta)
class ConsultaAdmin(SomenteLeituraAdmin):
    list_display = ('id', 'paciente', 'horario_gerado', 'ativo', 'criado_em')
    list_filter = ('ativo', 'criado_em')
