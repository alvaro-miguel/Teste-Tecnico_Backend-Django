from rest_framework import mixins, viewsets
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Especialidade, Agenda, HorarioGerado, Consulta
from .serializers import (
    EspecialidadeSerializer, 
    AgendaSerializer, 
    HorarioGeradoSerializer, 
    ConsultaSerializer
)
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Prefetch
from rest_framework.exceptions import ValidationError
from .services import agendar_consulta
from .permissions import (
    ConsultaPermission,
    IsEspecialistaOwner,
    IsInternoOrReadOnly,
    is_usuario_interno,
)
from django_filters.rest_framework import DjangoFilterBackend

@extend_schema_view(
    list=extend_schema(
        summary='Listar especialidades',
        description='Lista pública das especialidades ativas.',
        auth=[],
        tags=['Especialidades'],
    ),
    retrieve=extend_schema(
        summary='Consultar especialidade',
        description='Retorna uma especialidade ativa pelo identificador.',
        auth=[],
        tags=['Especialidades'],
    ),
    create=extend_schema(
        summary='Cadastrar especialidade',
        description='Operação restrita a usuários internos e superusuários.',
        tags=['Especialidades'],
    ),
    update=extend_schema(
        summary='Substituir especialidade',
        description='Operação restrita a usuários internos e superusuários.',
        tags=['Especialidades'],
    ),
    partial_update=extend_schema(
        summary='Alterar especialidade',
        description='Operação restrita a usuários internos e superusuários.',
        tags=['Especialidades'],
    ),
    destroy=extend_schema(
        summary='Desativar especialidade',
        description=(
            'Realiza exclusão lógica. Restrita a usuários internos e '
            'superusuários.'
        ),
        tags=['Especialidades'],
    ),
)
class EspecialidadeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsInternoOrReadOnly]
    queryset = Especialidade.objects.order_by('nome_especialidade', 'id')
    serializer_class = EspecialidadeSerializer


@extend_schema_view(
    list=extend_schema(
        summary='Listar minhas agendas',
        description='Lista somente as agendas do especialista autenticado.',
        tags=['Agendas'],
    ),
    retrieve=extend_schema(
        summary='Consultar minha agenda',
        description='Retorna uma agenda do especialista autenticado.',
        tags=['Agendas'],
    ),
    create=extend_schema(
        summary='Criar agenda',
        description=(
            'Cria uma agenda para o especialista autenticado e gera '
            'automaticamente os horários dos próximos 30 dias.'
        ),
        tags=['Agendas'],
    ),
    update=extend_schema(
        summary='Substituir agenda',
        description='Substitui uma agenda do especialista autenticado.',
        tags=['Agendas'],
    ),
    partial_update=extend_schema(
        summary='Alterar agenda',
        description=(
            'Altera uma agenda própria. A grade não pode ser alterada quando '
            'já existem reservas.'
        ),
        tags=['Agendas'],
    ),
    destroy=extend_schema(
        summary='Desativar agenda',
        description='Realiza a exclusão lógica da agenda e de seus horários.',
        tags=['Agendas'],
    ),
)
class AgendaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsEspecialistaOwner]
    queryset = (
        Agenda.objects
        .select_related('especialista__usuario', 'especialista__especialidade')
        .prefetch_related(
            Prefetch(
                'horarios',
                queryset=HorarioGerado.objects.order_by(
                    'data',
                    'horario_inicio',
                    'id',
                ),
            )
        )
        .order_by('dias_semana', 'hora_inicio_expediente', 'id')
    )
    serializer_class = AgendaSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and getattr(user, 'tipo_usuario', None) == 'ESPECIALISTA':
            return self.queryset.filter(especialista__usuario=user)
        return self.queryset.none()

    def perform_create(self, serializer):
        try:
            especialista = self.request.user.especialista_perfil
        except ObjectDoesNotExist as exc:
            raise ValidationError({
                'especialista': 'O usuário autenticado não possui perfil de especialista.'
            }) from exc

        serializer.save(especialista=especialista)
        

@extend_schema_view(
    list=extend_schema(
        summary='Listar horários',
        description=(
            'Lista pública dos horários ativos. Permite filtrar por status, '
            'data e especialista.'
        ),
        auth=[],
        tags=['Horários'],
    ),
    retrieve=extend_schema(
        summary='Consultar horário',
        description='Retorna um horário ativo pelo identificador.',
        auth=[],
        tags=['Horários'],
    ),
)
class HorarioGeradoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        HorarioGerado.objects
        .select_related(
            'agenda__especialista__usuario',
            'agenda__especialista__especialidade',
        )
        .filter(
            agenda__ativo=True,
            agenda__especialista__ativo=True,
            agenda__especialista__usuario__is_active=True,
        )
        .order_by('data', 'horario_inicio', 'id')
    )
    serializer_class = HorarioGeradoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'data', 'agenda__especialista']


@extend_schema_view(
    list=extend_schema(
        summary='Listar consultas acessíveis',
        description=(
            'Pacientes veem as próprias consultas; especialistas veem as '
            'consultas de suas agendas; usuários internos veem todas.'
        ),
        tags=['Consultas'],
    ),
    retrieve=extend_schema(
        summary='Consultar agendamento',
        description='Retorna uma consulta conforme o vínculo do usuário.',
        tags=['Consultas'],
    ),
    create=extend_schema(
        summary='Agendar consulta',
        description=(
            'Reserva um horário para o paciente autenticado. O paciente é '
            'definido pelo token JWT.'
        ),
        tags=['Consultas'],
    ),
)
class ConsultaViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [ConsultaPermission]
    queryset = (
        Consulta.objects
        .select_related(
            'paciente__usuario',
            'horario_gerado__agenda__especialista__usuario',
            'horario_gerado__agenda__especialista__especialidade',
        )
        .order_by(
            'horario_gerado__data',
            'horario_gerado__horario_inicio',
            'id',
        )
    )
    serializer_class = ConsultaSerializer

    def get_queryset(self):
        user = self.request.user
        if is_usuario_interno(user):
            return self.queryset.all()
        if getattr(user, 'tipo_usuario', None) == 'PACIENTE':
            return self.queryset.filter(paciente__usuario=user)
        if getattr(user, 'tipo_usuario', None) == 'ESPECIALISTA':
            return self.queryset.filter(
                horario_gerado__agenda__especialista__usuario=user
            )
        return self.queryset.none()

    def perform_create(self, serializer):
        try:
            paciente = self.request.user.paciente_perfil
        except ObjectDoesNotExist as exc:
            raise ValidationError({
                'paciente': 'O usuário autenticado não possui perfil de paciente.'
            }) from exc

        horario = serializer.validated_data.get('horario_gerado')
        
        consulta = agendar_consulta(paciente.id, horario.id)
        serializer.instance = consulta
