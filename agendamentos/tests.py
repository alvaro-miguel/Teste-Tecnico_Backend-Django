from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from usuarios.models import Usuario, Paciente, Especialista
from agendamentos.models import Especialidade, Agenda, HorarioGerado
from datetime import time, date
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
