from django.test import TestCase

from agendamentos.models import Especialidade


class SoftDeleteTestCase(TestCase):
    def test_delete_retorna_contrato_do_django(self):
        especialidade = Especialidade.objects.create(
            nome_especialidade='Cardiologia'
        )

        resultado = especialidade.delete()

        self.assertEqual(resultado, (1, {'agendamentos.Especialidade': 1}))
        self.assertFalse(Especialidade.objects.filter(pk=especialidade.pk).exists())
        self.assertTrue(
            Especialidade.all_objects.filter(
                pk=especialidade.pk,
                ativo=False,
            ).exists()
        )
        self.assertEqual(especialidade.delete(), (0, {}))

    def test_delete_de_queryset_executa_soft_delete(self):
        Especialidade.objects.bulk_create([
            Especialidade(nome_especialidade='Cardiologia'),
            Especialidade(nome_especialidade='Neurologia'),
        ])

        quantidade, detalhes = Especialidade.objects.all().delete()

        self.assertEqual(quantidade, 2)
        self.assertEqual(detalhes, {'agendamentos.Especialidade': 2})
        self.assertEqual(Especialidade.objects.count(), 0)
        self.assertEqual(Especialidade.all_objects.filter(ativo=False).count(), 2)
