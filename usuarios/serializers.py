from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import transaction
from rest_framework import serializers

from agendamentos.serializers import EspecialidadeSerializer
from .models import Especialista, Paciente, TipoUsuario, Usuario


class UsuarioCadastroSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[UnicodeUsernameValidator()],
    )
    password = serializers.CharField(
        write_only=True,
        required=False,
        validators=[validate_password],
    )

    class Meta:
        model = Usuario
        fields = [
            'username',
            'password',
            'first_name',
            'last_name',
            'email',
            'cpf',
            'telefone',
        ]
        extra_kwargs = {
            'cpf': {'validators': []},
        }


class PerfilSerializerMixin:
    tipo_usuario = None

    def validate_usuario(self, dados_usuario):
        usuario_atual = self.instance.usuario if self.instance else None
        usuario_id = usuario_atual.id if usuario_atual else None

        username = dados_usuario.get('username')
        if Usuario.objects.filter(username=username).exclude(id=usuario_id).exists():
            raise serializers.ValidationError({
                'username': 'Já existe um usuário com este nome.'
            })

        cpf = dados_usuario.get('cpf') or None
        dados_usuario['cpf'] = cpf
        if cpf and Usuario.objects.filter(cpf=cpf).exclude(id=usuario_id).exists():
            raise serializers.ValidationError({
                'cpf': 'Já existe um usuário com este CPF.'
            })

        if not usuario_atual and not dados_usuario.get('password'):
            raise serializers.ValidationError({
                'password': 'Este campo é obrigatório.'
            })

        return dados_usuario

    def criar_usuario(self, dados_usuario):
        senha = dados_usuario.pop('password')
        return Usuario.objects.create_user(
            password=senha,
            tipo_usuario=self.tipo_usuario,
            **dados_usuario,
        )

    def atualizar_usuario(self, usuario, dados_usuario):
        senha = dados_usuario.pop('password', None)
        for campo, valor in dados_usuario.items():
            setattr(usuario, campo, valor)

        usuario.tipo_usuario = self.tipo_usuario
        if senha:
            usuario.set_password(senha)
        usuario.save()


class PacienteSerializer(PerfilSerializerMixin, serializers.ModelSerializer):
    tipo_usuario = TipoUsuario.PACIENTE
    usuario = UsuarioCadastroSerializer(write_only=True)
    nome = serializers.CharField(source='usuario.first_name', read_only=True)
    telefone = serializers.CharField(source='usuario.telefone', read_only=True)

    class Meta:
        model = Paciente
        fields = [
            'id',
            'usuario',
            'nome',
            'telefone',
            'ativo',
            'criado_em',
            'atualizado_em',
        ]
        read_only_fields = ['ativo', 'criado_em', 'atualizado_em']

    @transaction.atomic
    def create(self, validated_data):
        usuario = self.criar_usuario(validated_data.pop('usuario'))
        return Paciente.objects.create(usuario=usuario, **validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        dados_usuario = validated_data.pop('usuario', None)
        if dados_usuario:
            self.atualizar_usuario(instance.usuario, dados_usuario)
        return super().update(instance, validated_data)


class EspecialistaSerializer(PerfilSerializerMixin, serializers.ModelSerializer):
    tipo_usuario = TipoUsuario.ESPECIALISTA
    usuario = UsuarioCadastroSerializer(write_only=True)
    especialidade_detalhe = EspecialidadeSerializer(
        source='especialidade',
        read_only=True,
    )
    nome = serializers.CharField(source='usuario.first_name', read_only=True)

    class Meta:
        model = Especialista
        fields = [
            'id',
            'usuario',
            'nome',
            'crm',
            'especialidade',
            'especialidade_detalhe',
            'ativo',
            'criado_em',
            'atualizado_em',
        ]
        read_only_fields = ['ativo', 'criado_em', 'atualizado_em']

    @transaction.atomic
    def create(self, validated_data):
        usuario = self.criar_usuario(validated_data.pop('usuario'))
        return Especialista.objects.create(usuario=usuario, **validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        dados_usuario = validated_data.pop('usuario', None)
        if dados_usuario:
            self.atualizar_usuario(instance.usuario, dados_usuario)
        return super().update(instance, validated_data)
