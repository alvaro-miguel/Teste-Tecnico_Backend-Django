
from datetime import datetime, date, timedelta
from .models import Agenda, HorarioGerado, Consulta, StatusHorario
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError


CAMPOS_GRADE_AGENDA = {
    'dias_semana',
    'hora_inicio_expediente',
    'hora_fim_expediente',
    'quantidade_vagas_dia',
}


def _bloquear_especialista(especialista_id):
    from usuarios.models import Especialista

    return Especialista.objects.select_for_update().get(pk=especialista_id)


def _validar_agenda(agenda):
    try:
        agenda.full_clean()
    except DjangoValidationError as exc:
        raise ValidationError(exc.message_dict) from exc

def gerar_horarios(agenda):
    _validar_agenda(agenda)

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


@transaction.atomic
def criar_agenda(**dados_agenda):
    agenda = Agenda(**dados_agenda)
    agenda.especialista = _bloquear_especialista(agenda.especialista_id)
    _validar_agenda(agenda)
    agenda.save()
    gerar_horarios(agenda)
    return agenda


@transaction.atomic
def atualizar_agenda(instance, dados_agenda):
    _bloquear_especialista(instance.especialista_id)
    agenda = Agenda.objects.select_for_update().get(pk=instance.pk)
    grade_alterada = any(
        campo in dados_agenda and getattr(agenda, campo) != dados_agenda[campo]
        for campo in CAMPOS_GRADE_AGENDA
    )

    if grade_alterada:
        horarios = (
            HorarioGerado.all_objects
            .select_for_update()
            .filter(agenda=agenda)
        )
        possui_reserva = (
            horarios.filter(status=StatusHorario.RESERVADO).exists()
            or Consulta.all_objects.filter(horario_gerado__agenda=agenda).exists()
        )
        if possui_reserva:
            raise ValidationError({
                'agenda': (
                    'Não é possível alterar a grade de uma agenda que possui reservas.'
                )
            })

    for campo, valor in dados_agenda.items():
        setattr(agenda, campo, valor)

    _validar_agenda(agenda)
    agenda.save()

    if grade_alterada:
        HorarioGerado.objects.filter(agenda=agenda).update(ativo=False)
        gerar_horarios(agenda)

    return agenda


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
