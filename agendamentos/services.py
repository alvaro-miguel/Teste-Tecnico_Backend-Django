
from datetime import datetime, date, timedelta
from .models import HorarioGerado
from django.db import transaction
from django.core.exceptions import ValidationError

def gerar_horarios(agenda):
    data_base = date.today()
    inicio = datetime.combine(data_base, agenda.hora_inicio_expediente)
    fim = datetime.combine(data_base, agenda.hora_fim_expediente)

    diferenca = fim - inicio
    minutos_totais = int(diferenca.total_seconds() / 60)

    duracao_min_vaga = minutos_totais // agenda.quantidade_vagas_dia

    horarios_criar = []
    tempo_atual = inicio

    for _ in range(agenda.quantidade_vagas_dia):
        proximo_tempo = tempo_atual + timedelta(minutes=duracao_min_vaga)

        horario = HorarioGerado(
            agenda=agenda,
            horario_inicio = tempo_atual.time(),
            horario_fim = proximo_tempo.time(),
            status='DISPONIVEL'
        )

        horarios_criar.append(horario)

        tempo_atual = proximo_tempo

    HorarioGerado.objects.bulk_create(horarios_criar)


def agendar_consulta(paciente_id, horario_id):
    with transaction.atomic():
        horario = HorarioGerado.objects.select_for_update().get(id=horario_id)

        if horario.status != 'DISPONIVEL':
            raise ValidationError("Este horário não está disponível")

        horario.status = 'RESERVADO'
        horario.save()

        consulta = consulta.objects.create(
            paciente_id = paciente_id,
            horario_gerado = horario
        )
