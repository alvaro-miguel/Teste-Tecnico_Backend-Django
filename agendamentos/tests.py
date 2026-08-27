from rest_framework.test import APITestCase, APITransactionTestCase
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.urls import reverse
from django.test import skipUnlessDBFeature
from usuarios.models import Usuario, Paciente, Especialista
from agendamentos.models import Especialidade, Agenda, HorarioGerado
from datetime import time, date
import concurrent.futures
from unittest.mock import patch

from agendamentos.services import agendar_consulta, atualizar_agenda, criar_agenda
from django.db import IntegrityError, connection, transaction
# Create your tests here.

class AgendamentoTestCase(APITestCase):
    
    def setUp(self):
        self.usuario_paciente = Usuario.objects.create_user(username='paciente1', password='123', tipo_usuario='PACIENTE')
        self.paciente = Paciente.objects.create(usuario=self.usuario_paciente)

        self.usuario_especialista = Usuario.objects.create_user(username='dr_julio', password='123', tipo_usuario='ESPECIALISTA')
        self.especialidade = Especialidade.objects.create(nome_especialidade='Cardiologia')
        self.especialista = Especialista.objects.create(usuario=self.usuario_especialista, especialidade=self.especialidade, crm='12345')

        self.agenda = Agenda.objects.create(
            especialista=self.especialista, 
            dias_semana=0, 
            hora_inicio_expediente=time(8, 0), 
            hora_fim_expediente=time(18, 0), 
            quantidade_vagas_dia=10
        )
        
        self.horario = HorarioGerado.objects.create(
            agenda=self.agenda,
            data=date(2025, 1, 1),
            horario_inicio=time(8, 0),
            horario_fim=time(9, 0),
            status='DISPONIVEL'
        )
        
        self.client.force_authenticate(user=self.usuario_paciente)
        self.url_consulta = reverse('consulta-list') 

    def test_paciente_agendar_horario_livre(self):
        payload = {
            "paciente": self.paciente.id,
            "horario_gerado": self.horario.id
        }
        response = self.client.post(self.url_consulta, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.horario.refresh_from_db()
        self.assertEqual(self.horario.status, 'RESERVADO')


    def test_paciente_nao_agendar_horario_ocupado(self):
        self.horario.status = 'RESERVADO'
        self.horario.save()

        payload = {
            "paciente": self.paciente.id,
            "horario_gerado": self.horario.id
        }
        
        response = self.client.post(self.url_consulta, payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('erro', response.data) 


    def test_geracao_horarios_automaticos(self):
        self.client.force_authenticate(user=self.usuario_especialista)
        url_agenda = reverse('agenda-list')

        payload = {
            "especialista":self.especialista.id,
            "dias_semana":1,
            "hora_inicio_expediente":"08:00:00",
            "hora_fim_expediente":"10:01:00",
            "quantidade_vagas_dia":4
        }

        response = self.client.post(url_agenda, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        horarios_gerados = HorarioGerado.objects.filter(
            agenda_id=response.data['id']
        ).order_by('data', 'horario_inicio')
        self.assertGreater(horarios_gerados.count(), 0, "Nenhum horário foi gerado")

        datas_geradas = horarios_gerados.values_list('data', flat=True).distinct()
        for data_horario in datas_geradas:
            horarios_do_dia = list(horarios_gerados.filter(data=data_horario))
            self.assertEqual(len(horarios_do_dia), 4)
            self.assertEqual(horarios_do_dia[0].horario_inicio, time(8, 0))
            self.assertEqual(horarios_do_dia[-1].horario_fim, time(10, 1))
            self.assertTrue(all(
                atual.horario_fim == seguinte.horario_inicio
                for atual, seguinte in zip(horarios_do_dia, horarios_do_dia[1:])
            ))

    def test_rejeita_agenda_com_intervalo_invalido(self):
        self.client.force_authenticate(user=self.usuario_especialista)
        response = self.client.post(reverse('agenda-list'), {
            'dias_semana': 1,
            'hora_inicio_expediente': '10:00:00',
            'hora_fim_expediente': '08:00:00',
            'quantidade_vagas_dia': 4,
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('hora_fim_expediente', response.data)

    def test_rejeita_quantidade_de_vagas_que_gera_horario_vazio(self):
        self.client.force_authenticate(user=self.usuario_especialista)
        response = self.client.post(reverse('agenda-list'), {
            'dias_semana': 1,
            'hora_inicio_expediente': '08:00:00',
            'hora_fim_expediente': '08:00:01',
            'quantidade_vagas_dia': 2,
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('quantidade_vagas_dia', response.data)

    def test_banco_rejeita_horario_duplicado(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            HorarioGerado.objects.create(
                agenda=self.agenda,
                data=self.horario.data,
                horario_inicio=self.horario.horario_inicio,
                horario_fim=self.horario.horario_fim,
            )

    def test_banco_rejeita_horario_com_fim_anterior_ao_inicio(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            HorarioGerado.objects.create(
                agenda=self.agenda,
                data=date(2025, 1, 2),
                horario_inicio=time(10, 0),
                horario_fim=time(9, 0),
            )

    def test_nao_agenda_horario_de_agenda_inativa(self):
        self.agenda.delete()

        response = self.client.post(self.url_consulta, {
            'horario_gerado': self.horario.id,
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('horario_gerado', response.data)

    def test_atualizacao_da_agenda_regenera_horarios_disponiveis(self):
        self.client.force_authenticate(user=self.usuario_especialista)
        response_criacao = self.client.post(reverse('agenda-list'), {
            'dias_semana': 1,
            'hora_inicio_expediente': '08:00:00',
            'hora_fim_expediente': '10:00:00',
            'quantidade_vagas_dia': 2,
        })
        self.assertEqual(response_criacao.status_code, status.HTTP_201_CREATED)

        agenda_id = response_criacao.data['id']
        ids_horarios_antigos = list(
            HorarioGerado.objects
            .filter(agenda_id=agenda_id)
            .values_list('id', flat=True)
        )

        response_atualizacao = self.client.patch(
            reverse('agenda-detail', args=[agenda_id]),
            {
                'hora_inicio_expediente': '09:00:00',
                'hora_fim_expediente': '11:00:00',
            },
        )

        self.assertEqual(
            response_atualizacao.status_code,
            status.HTTP_200_OK,
            response_atualizacao.data,
        )
        self.assertFalse(
            HorarioGerado.objects.filter(id__in=ids_horarios_antigos).exists()
        )
        self.assertEqual(
            HorarioGerado.all_objects.filter(
                id__in=ids_horarios_antigos,
                ativo=False,
            ).count(),
            len(ids_horarios_antigos),
        )
        novos_horarios = HorarioGerado.objects.filter(agenda_id=agenda_id)
        self.assertGreater(novos_horarios.count(), 0)
        self.assertTrue(all(
            horario.horario_inicio >= time(9, 0)
            and horario.horario_fim <= time(11, 0)
            for horario in novos_horarios
        ))

    def test_rejeita_alteracao_de_agenda_com_reserva(self):
        self.client.force_authenticate(user=self.usuario_especialista)
        response_criacao = self.client.post(reverse('agenda-list'), {
            'dias_semana': 1,
            'hora_inicio_expediente': '08:00:00',
            'hora_fim_expediente': '10:00:00',
            'quantidade_vagas_dia': 2,
        })
        agenda_id = response_criacao.data['id']
        horario = HorarioGerado.objects.filter(agenda_id=agenda_id).first()
        horario.status = 'RESERVADO'
        horario.save(update_fields=['status'])

        response = self.client.patch(
            reverse('agenda-detail', args=[agenda_id]),
            {'hora_inicio_expediente': '09:00:00'},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            response.data,
        )
        self.assertIn('agenda', response.data)
        self.assertEqual(
            Agenda.objects.get(id=agenda_id).hora_inicio_expediente,
            time(8, 0),
        )

    @patch('agendamentos.services.gerar_horarios')
    def test_falha_na_geracao_desfaz_criacao_da_agenda(self, gerar_mock):
        gerar_mock.side_effect = RuntimeError('Falha simulada na geração')
        quantidade_inicial = Agenda.objects.count()

        with self.assertRaises(RuntimeError):
            criar_agenda(
                especialista=self.especialista,
                dias_semana=1,
                hora_inicio_expediente=time(8, 0),
                hora_fim_expediente=time(10, 0),
                quantidade_vagas_dia=2,
            )

        self.assertEqual(Agenda.objects.count(), quantidade_inicial)

    def test_falha_na_regeneracao_desfaz_atualizacao_da_agenda(self):
        agenda = criar_agenda(
            especialista=self.especialista,
            dias_semana=1,
            hora_inicio_expediente=time(8, 0),
            hora_fim_expediente=time(10, 0),
            quantidade_vagas_dia=2,
        )
        ids_horarios = list(
            HorarioGerado.objects
            .filter(agenda=agenda)
            .values_list('id', flat=True)
        )

        with patch(
            'agendamentos.services.gerar_horarios',
            side_effect=RuntimeError('Falha simulada na regeneração'),
        ):
            with self.assertRaises(RuntimeError):
                atualizar_agenda(agenda, {
                    'hora_inicio_expediente': time(9, 0),
                    'hora_fim_expediente': time(11, 0),
                })

        agenda.refresh_from_db()
        self.assertEqual(agenda.hora_inicio_expediente, time(8, 0))
        self.assertEqual(agenda.hora_fim_expediente, time(10, 0))
        self.assertEqual(
            HorarioGerado.objects.filter(id__in=ids_horarios).count(),
            len(ids_horarios),
        )


class RaceConditionCase(APITransactionTestCase):
    def setUp(self):
        self.usuario_paciente1 = Usuario.objects.create_user(username='paciente1', password='123', tipo_usuario='PACIENTE')
        self.paciente1 = Paciente.objects.create(usuario=self.usuario_paciente1)

        self.usuario_paciente2 = Usuario.objects.create_user(username='paciente2', password='123', tipo_usuario='PACIENTE')
        self.paciente2 = Paciente.objects.create(usuario=self.usuario_paciente2)

        self.usuario_especialista = Usuario.objects.create_user(username='dr_julio', password='123', tipo_usuario='ESPECIALISTA')
        self.especialidade = Especialidade.objects.create(nome_especialidade='Cardiologia')
        self.especialista = Especialista.objects.create(usuario=self.usuario_especialista, especialidade=self.especialidade, crm='12345')

        self.agenda = Agenda.objects.create(
            especialista = self.especialista, dias_semana = 0, hora_inicio_expediente=time(8, 0), hora_fim_expediente=time(18,0), quantidade_vagas_dia=10
        )

        self.horario = HorarioGerado.objects.create(
            agenda=self.agenda, data=date(2025, 1, 1),
            horario_inicio = time(8,0), horario_fim=time(9,0), status='DISPONIVEL'
        )


    @skipUnlessDBFeature('has_select_for_update')
    def test_duplo_agendamento(self):

        def tentativa_agendamento(paciente_id, horario_id):
            try:
                agendar_consulta(paciente_id, horario_id)
                return True
            except ValidationError:
                return False
            finally:
                connection.close()
                

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futuro1 = executor.submit(tentativa_agendamento, self.paciente1.id, self.horario.id)
            futuro2 = executor.submit(tentativa_agendamento, self.paciente2.id, self.horario.id)

            sucesso1 = futuro1.result()
            sucesso2 = futuro2.result()

            self.assertTrue(sucesso1 != sucesso2, "Falha crítica: Dois pacientes reservaram a mesma vaga simultaneamente")

            from agendamentos.models import Consulta
            consultas_criadas = Consulta.objects.filter(horario_gerado=self.horario).count()
            self.assertEqual(consultas_criadas, 1)
