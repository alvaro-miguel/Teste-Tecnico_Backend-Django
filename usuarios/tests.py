from datetime import time

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from agendamentos.models import Agenda, Especialidade, HorarioGerado
from usuarios.models import Especialista, Paciente, TipoUsuario, Usuario


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


class ValidacaoCadastroAPITestCase(APITestCase):
    def setUp(self):
        self.usuario_interno = Usuario.objects.create_user(
            username='interno',
            password='SenhaForte@2026',
            tipo_usuario=TipoUsuario.INTERNO,
        )
        self.client.force_authenticate(self.usuario_interno)
        self.especialidade = Especialidade.objects.create(
            nome_especialidade='Cardiologia'
        )

    def dados_usuario(self, **alteracoes):
        dados = {
            'username': 'paciente.teste',
            'password': 'SenhaForte@2026',
            'first_name': '  Maria   da Silva  ',
            'last_name': '  Souza   Lima  ',
            'email': '  MARIA@EXAMPLE.COM ',
            'cpf': '529.982.247-25',
            'telefone': '(11) 98765-4321',
        }
        dados.update(alteracoes)
        return dados

    def test_cadastro_normaliza_dados_do_paciente(self):
        resposta = self.client.post(
            reverse('paciente-list'),
            {'usuario': self.dados_usuario()},
            format='json',
        )

        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        paciente = Paciente.objects.get(pk=resposta.data['id'])
        self.assertEqual(paciente.usuario.first_name, 'Maria da Silva')
        self.assertEqual(paciente.usuario.last_name, 'Souza Lima')
        self.assertEqual(paciente.usuario.email, 'maria@example.com')
        self.assertEqual(paciente.usuario.cpf, '52998224725')
        self.assertEqual(paciente.usuario.telefone, '11987654321')

    def test_rejeita_cpf_invalido(self):
        resposta = self.client.post(
            reverse('paciente-list'),
            {'usuario': self.dados_usuario(cpf='111.111.111-11')},
            format='json',
        )

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cpf', resposta.data['usuario'])

    def test_rejeita_cpf_duplicado_com_formatacao_diferente(self):
        Usuario.objects.create_user(
            username='cpf.existente',
            cpf='52998224725',
        )

        resposta = self.client.post(
            reverse('paciente-list'),
            {'usuario': self.dados_usuario()},
            format='json',
        )

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cpf', resposta.data['usuario'])

    def test_rejeita_telefone_sem_ddd(self):
        resposta = self.client.post(
            reverse('paciente-list'),
            {'usuario': self.dados_usuario(telefone='98765-4321')},
            format='json',
        )

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('telefone', resposta.data['usuario'])

    def test_rejeita_nome_composto_apenas_por_espacos(self):
        resposta = self.client.post(
            reverse('paciente-list'),
            {'usuario': self.dados_usuario(first_name='   ')},
            format='json',
        )

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('first_name', resposta.data['usuario'])

    def test_rejeita_username_duplicado_independentemente_da_caixa(self):
        Usuario.objects.create_user(username='Paciente.Teste')

        resposta = self.client.post(
            reverse('paciente-list'),
            {'usuario': self.dados_usuario()},
            format='json',
        )

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', resposta.data['usuario'])

    def test_normaliza_crm_do_especialista(self):
        resposta = self.client.post(
            reverse('especialista-list'),
            {
                'usuario': self.dados_usuario(username='especialista'),
                'crm': 'CRM-SP 0012345',
                'especialidade': self.especialidade.pk,
            },
            format='json',
        )

        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        especialista = Especialista.objects.get(pk=resposta.data['id'])
        self.assertEqual(especialista.crm, '12345/SP')

    def test_rejeita_crm_invalido(self):
        resposta = self.client.post(
            reverse('especialista-list'),
            {
                'usuario': self.dados_usuario(username='especialista'),
                'crm': '12345/XX',
                'especialidade': self.especialidade.pk,
            },
            format='json',
        )

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('crm', resposta.data)

    def test_rejeita_crm_normalizado_duplicado(self):
        usuario = Usuario.objects.create_user(username='especialista.existente')
        Especialista.objects.create(
            usuario=usuario,
            crm='12345/SP',
            especialidade=self.especialidade,
        )

        resposta = self.client.post(
            reverse('especialista-list'),
            {
                'usuario': self.dados_usuario(username='especialista'),
                'crm': 'CRM-SP 12345',
                'especialidade': self.especialidade.pk,
            },
            format='json',
        )

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('crm', resposta.data)

    def test_normaliza_nome_e_rejeita_especialidade_duplicada_sem_case(self):
        resposta_criacao = self.client.post(
            reverse('especialidade-list'),
            {'nome_especialidade': '  Cirurgia   Geral  '},
            format='json',
        )
        resposta_duplicada = self.client.post(
            reverse('especialidade-list'),
            {'nome_especialidade': 'cirurgia geral'},
            format='json',
        )

        self.assertEqual(resposta_criacao.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            resposta_criacao.data['nome_especialidade'],
            'Cirurgia Geral',
        )
        self.assertEqual(
            resposta_duplicada.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn('nome_especialidade', resposta_duplicada.data)

    def test_listagem_de_pacientes_evitar_n_mais_um(self):
        for indice in range(5):
            usuario = Usuario.objects.create_user(
                username=f'paciente.performance.{indice}',
                first_name=f'Paciente {indice}',
            )
            Paciente.objects.create(usuario=usuario)

        with self.assertNumQueries(2):
            resposta = self.client.get(reverse('paciente-list'))

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data['count'], 5)

    def test_listagem_de_especialistas_evitar_n_mais_um(self):
        for indice in range(5):
            usuario = Usuario.objects.create_user(
                username=f'especialista.performance.{indice}',
                first_name=f'Especialista {indice}',
            )
            Especialista.objects.create(
                usuario=usuario,
                especialidade=self.especialidade,
                crm=f'PERFORMANCE-{indice}',
            )

        with self.assertNumQueries(2):
            resposta = self.client.get(reverse('especialista-list'))

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data['count'], 5)
