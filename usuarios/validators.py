import re

from django.core.exceptions import ValidationError


UFS_BRASILEIRAS = {
    'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS',
    'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC',
    'SP', 'SE', 'TO',
}


def normalizar_texto(valor):
    if valor is None:
        return valor
    return ' '.join(valor.split())


def normalizar_cpf(valor):
    if not valor:
        return None

    cpf = re.sub(r'\D', '', valor)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        raise ValidationError('Informe um CPF válido.')

    for tamanho in (9, 10):
        soma = sum(
            int(digito) * peso
            for digito, peso in zip(cpf[:tamanho], range(tamanho + 1, 1, -1))
        )
        digito_verificador = (soma * 10 % 11) % 10
        if digito_verificador != int(cpf[tamanho]):
            raise ValidationError('Informe um CPF válido.')

    return cpf


def normalizar_telefone(valor):
    if not valor:
        return None

    telefone = re.sub(r'\D', '', valor)
    if len(telefone) not in (10, 11) or telefone == telefone[0] * len(telefone):
        raise ValidationError(
            'Informe um telefone brasileiro com DDD e 10 ou 11 dígitos.'
        )
    return telefone


def normalizar_crm(valor):
    if not valor:
        raise ValidationError('Este campo é obrigatório.')

    crm = re.sub(r'^CRM\s*[-/]?\s*', '', valor.strip().upper())
    numeros = re.findall(r'\d+', crm)
    ufs = re.findall(r'[A-Z]{2}', crm)

    if len(numeros) != 1 or len(ufs) != 1:
        raise ValidationError('Informe o CRM no formato número/UF.')

    numero, uf = numeros[0], ufs[0]
    caracteres_restantes = re.sub(r'[\dA-Z\s/-]', '', crm)
    if (
        caracteres_restantes
        or not 1 <= len(numero) <= 10
        or uf not in UFS_BRASILEIRAS
    ):
        raise ValidationError('Informe o CRM no formato número/UF.')

    return f'{int(numero)}/{uf}'
