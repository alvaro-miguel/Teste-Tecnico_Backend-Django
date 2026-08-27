from rest_framework import viewsets
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Especialista, Paciente
from .serializers import EspecialistaSerializer, PacienteSerializer
from agendamentos.permissions import IsInterno, IsInternoOrReadOnly

@extend_schema_view(
    list=extend_schema(
        summary='Listar especialistas',
        description='Lista pública dos especialistas ativos.',
        auth=[],
        tags=['Especialistas'],
    ),
    retrieve=extend_schema(
        summary='Consultar especialista',
        description='Retorna os dados públicos de um especialista ativo.',
        auth=[],
        tags=['Especialistas'],
    ),
    create=extend_schema(
        summary='Credenciar especialista',
        description='Operação restrita a usuários internos e superusuários.',
        tags=['Especialistas'],
    ),
    update=extend_schema(
        summary='Substituir especialista',
        description='Operação restrita a usuários internos e superusuários.',
        tags=['Especialistas'],
    ),
    partial_update=extend_schema(
        summary='Alterar especialista',
        description='Operação restrita a usuários internos e superusuários.',
        tags=['Especialistas'],
    ),
    destroy=extend_schema(
        summary='Desativar especialista',
        description=(
            'Realiza exclusão lógica. Restrita a usuários internos e '
            'superusuários.'
        ),
        tags=['Especialistas'],
    ),
)
class EspecialistaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsInternoOrReadOnly]
    queryset = (
        Especialista.objects
        .select_related('usuario', 'especialidade')
        .order_by('usuario__first_name', 'id')
    )
    serializer_class = EspecialistaSerializer

@extend_schema_view(
    list=extend_schema(
        summary='Listar pacientes',
        description='Operação restrita a usuários internos e superusuários.',
        tags=['Pacientes'],
    ),
    retrieve=extend_schema(
        summary='Consultar paciente',
        description='Operação restrita a usuários internos e superusuários.',
        tags=['Pacientes'],
    ),
    create=extend_schema(
        summary='Cadastrar paciente',
        description='Operação restrita a usuários internos e superusuários.',
        tags=['Pacientes'],
    ),
    update=extend_schema(
        summary='Substituir paciente',
        description='Operação restrita a usuários internos e superusuários.',
        tags=['Pacientes'],
    ),
    partial_update=extend_schema(
        summary='Alterar paciente',
        description='Operação restrita a usuários internos e superusuários.',
        tags=['Pacientes'],
    ),
    destroy=extend_schema(
        summary='Desativar paciente',
        description=(
            'Realiza exclusão lógica. Restrita a usuários internos e '
            'superusuários.'
        ),
        tags=['Pacientes'],
    ),
)
class PacienteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsInterno]
    queryset = (
        Paciente.objects
        .select_related('usuario')
        .order_by('usuario__first_name', 'id')
    )
    serializer_class = PacienteSerializer
