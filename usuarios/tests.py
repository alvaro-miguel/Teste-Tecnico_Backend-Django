from datetime import time

from django.test import TestCase

from agendamentos.models import Agenda, Especialidade, HorarioGerado
from usuarios.models import Especialista, Paciente, Usuario


class SoftDeletePerfisTestCase(TestCase):
    def test_delete_em_lote_desativa_pacientes_e_usuarios(self):
        usuarios = [
            Usuario.objects.create_user(username='paciente1'),
            Usuario.objects.create_user(username='paciente2'),
        ]
        Paciente.objects.bulk_create([
            Paciente(usuario=usuarios[0]),
            Paciente(usuario=usuarios[1]),
        ])

        quantidade, detalhes = Paciente.objects.all().delete()

        self.assertEqual(quantidade, 2)
        self.assertEqual(detalhes, {'usuarios.Paciente': 2})
        self.assertEqual(Paciente.objects.count(), 0)
        self.assertFalse(
            Usuario.objects.filter(pk__in=[u.pk for u in usuarios], is_active=True)
            .exists()
        )

    def test_delete_de_especialista_desativa_agendas_horarios_e_usuario(self):
        usuario = Usuario.objects.create_user(username='especialista')
        especialidade = Especialidade.objects.create(
            nome_especialidade='Cardiologia'
        )
        especialista = Especialista.objects.create(
            usuario=usuario,
            especialidade=especialidade,
            crm='CRM-1',
        )
        agenda = Agenda.objects.create(
            especialista=especialista,
            dias_semana=0,
            hora_inicio_expediente=time(8, 0),
            hora_fim_expediente=time(9, 0),
            quantidade_vagas_dia=1,
        )
        horario = HorarioGerado.objects.create(
            agenda=agenda,
            data='2026-09-01',
            horario_inicio=time(8, 0),
            horario_fim=time(9, 0),
        )

        quantidade, detalhes = Especialista.objects.filter(
            pk=especialista.pk
        ).delete()

        self.assertEqual(quantidade, 3)
        self.assertEqual(detalhes['usuarios.Especialista'], 1)
        self.assertEqual(detalhes['agendamentos.Agenda'], 1)
        self.assertEqual(detalhes['agendamentos.HorarioGerado'], 1)
        usuario.refresh_from_db()
        self.assertFalse(usuario.is_active)
        self.assertFalse(Agenda.objects.filter(pk=agenda.pk).exists())
        self.assertFalse(HorarioGerado.objects.filter(pk=horario.pk).exists())
