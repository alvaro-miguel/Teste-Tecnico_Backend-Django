# API de Agendamentos Médicos

Backend de um sistema de agendamentos médicos desenvolvido com Django e Django REST Framework. A aplicação administra especialidades, especialistas, pacientes e agendas, gera horários automaticamente e protege a reserva de uma mesma vaga contra concorrência.

## Tecnologias

- Python 3.12
- Django e Django REST Framework
- PostgreSQL
- JWT com Simple JWT
- Filtros e paginação com `django-filter`
- OpenAPI e Swagger UI com `drf-spectacular`
- Docker e Docker Compose

## Execução com Docker

Pré-requisito: Docker com o comando `docker compose` disponível.

1. Crie o arquivo de configuração:

```bash
cp .env.example .env
```

No PowerShell, use:

```powershell
Copy-Item .env.example .env
```

2. Revise ao menos o valor de `SECRET_KEY` no `.env`.

3. Construa e inicie os serviços:

```bash
docker compose up --build
```

O container `web` aguarda o PostgreSQL ficar saudável, executa as migrations e inicia a API em `http://127.0.0.1:8000/`.

Com os containers ativos, os comandos administrativos podem ser executados assim:

```bash
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py test
docker compose exec web python manage.py spectacular --validate --fail-on-warn
```

Para encerrar:

```bash
docker compose down
```

Use `docker compose down -v` somente quando também quiser apagar definitivamente os dados locais do PostgreSQL.

## Execução local

Pré-requisitos: Python 3.12 e PostgreSQL acessível localmente.

1. Crie e ative o ambiente virtual:

```bash
python -m venv venv
```

No PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

No Linux ou macOS:

```bash
source venv/bin/activate
```

2. Instale as dependências e configure o ambiente:

```bash
pip install -r requirements.txt
cp .env.example .env
```

3. Ajuste no `.env` as credenciais do seu PostgreSQL. Para execução local, mantenha `POSTGRES_HOST=localhost`.

4. Execute a aplicação:

```bash
python manage.py migrate
python manage.py test
python manage.py runserver
```

## Variáveis de ambiente

| Variável | Finalidade | Padrão de desenvolvimento |
| --- | --- | --- |
| `SECRET_KEY` | Chave criptográfica do Django | chave local insegura |
| `DEBUG` | Ativa o modo de depuração | `True` |
| `ALLOWED_HOSTS` | Hosts separados por vírgula | `localhost,127.0.0.1` |
| `TIME_ZONE` | Fuso horário da aplicação | `America/Sao_Paulo` |
| `POSTGRES_DB` | Nome do banco | `agendamentos_db` |
| `POSTGRES_USER` | Usuário do banco | `usuario_db` |
| `POSTGRES_PASSWORD` | Senha do banco | `senha123` |
| `POSTGRES_HOST` | Host do banco | `localhost`; o Compose força `db` |
| `POSTGRES_PORT` | Porta do banco | `5432` |

Os valores padrão servem apenas para desenvolvimento. Em outro ambiente, use uma `SECRET_KEY` forte, `DEBUG=False` e credenciais próprias.

## Autenticação

Obtenha e renove tokens JWT pelas rotas:

- `POST /api/token/`
- `POST /api/token/refresh/`

Nas rotas protegidas, envie:

```http
Authorization: Bearer <access_token>
```

## Rotas e permissões

As rotas de detalhe usam o formato correspondente com `/{id}/`.

| Recurso | Operações | Acesso |
| --- | --- | --- |
| `/api/usuarios/especialistas/` | leitura | público |
| `/api/usuarios/especialistas/` | criação e alterações | usuário `INTERNO` ou superusuário |
| `/api/usuarios/pacientes/` | CRUD | usuário `INTERNO` ou superusuário |
| `/api/agendamentos/especialidades/` | leitura | público |
| `/api/agendamentos/especialidades/` | criação e alterações | usuário `INTERNO` ou superusuário |
| `/api/agendamentos/agendas/` | CRUD | especialista autenticado, limitado às próprias agendas |
| `/api/agendamentos/horarios/` | leitura | público |
| `/api/agendamentos/consultas/` | criação | paciente autenticado |
| `/api/agendamentos/consultas/` | leitura | paciente, especialista relacionado, `INTERNO` ou superusuário |

Consultas não podem ser alteradas ou excluídas pela API. A criação associa automaticamente o paciente autenticado, e a criação da agenda associa automaticamente o especialista autenticado.

### Filtros de horários

O endpoint de horários aceita `status`, `data` e `agenda__especialista`:

```text
/api/agendamentos/horarios/?status=DISPONIVEL&data=2026-09-01
```

As listagens são paginadas em 20 registros por página.

## OpenAPI e Swagger

Com a API ativa:

- Swagger UI: `http://127.0.0.1:8000/api/docs/`
- Esquema OpenAPI: `http://127.0.0.1:8000/api/schema/`

Para validar o esquema sem iniciar o servidor:

```bash
python manage.py spectacular --validate --fail-on-warn
```

## Regras principais

- Uma agenda pertence ao especialista autenticado.
- Os horários são distribuídos igualmente dentro do expediente informado.
- Horários duplicados para a mesma agenda, data e início são impedidos pelo banco.
- Uma reserva altera o horário de `DISPONIVEL` para `RESERVADO`.
- A reserva utiliza transação e bloqueio de linha para impedir agendamentos concorrentes.
- Entidades com soft delete deixam de aparecer nos querysets ativos.
