
from datetime import datetime, date, timedelta
from .models import HorarioGerado, Consulta, StatusHorario
from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError

def gerar_horarios(agenda):
    agenda.full_clean()

    data_base = date.today()
    horarios_criar = []

    for i in range(30):
        dia_atual = data_base + timedelta(days=i)

        if dia_atual.weekday() == agenda.dias_semana:
            inicio = datetime.combine(dia_atual, agenda.hora_inicio_expediente)
            fim = datetime.combine(dia_atual, agenda.hora_fim_expediente)

            diferenca = fim - inicio
            for indice in range(agenda.quantidade_vagas_dia):
                tempo_atual = inicio + (
                    diferenca * indice / agenda.quantidade_vagas_dia
                )
                proximo_tempo = inicio + (
                    diferenca * (indice + 1) / agenda.quantidade_vagas_dia
                )

                horario = HorarioGerado(
                    agenda=agenda,
                    data=dia_atual,
                    horario_inicio = tempo_atual.time(),
                    horario_fim = proximo_tempo.time(),
                    status=StatusHorario.DISPONIVEL
                )

                horarios_criar.append(horario)

    HorarioGerado.objects.bulk_create(horarios_criar)


def agendar_consulta(paciente_id, horario_id):
    with transaction.atomic():
        try:
            horario = (
                HorarioGerado.objects
                .select_for_update()
                .get(
                    id=horario_id,
                    agenda__ativo=True,
                    agenda__especialista__ativo=True,
                    agenda__especialista__usuario__is_active=True,
                )
            )
        except HorarioGerado.DoesNotExist as exc:
            raise ValidationError({
                'horario_gerado': 'Horário não encontrado ou indisponível.'
            }) from exc

        if horario.status != StatusHorario.DISPONIVEL:
            raise ValidationError({'erro': 'Este horário não está disponível.'})

        horario.status = StatusHorario.RESERVADO
        horario.save(update_fields=['status', 'atualizado_em'])

        try:
            consulta = Consulta.objects.create(
                paciente_id=paciente_id,
                horario_gerado=horario,
            )
        except IntegrityError as exc:
            raise ValidationError({
                'erro': 'Este horário não está disponível.'
            }) from exc

        return consulta
