# Clínica Agenda — Django REST + Vue

Aplicação completa para administrar especialidades, especialistas, pacientes, agendas e consultas médicas. O backend gera automaticamente as vagas de cada agenda, usa autenticação JWT, aplica exclusão lógica aos registros e protege reservas concorrentes com transações e bloqueios no PostgreSQL. O frontend responsivo em Vue oferece uma experiência específica para pacientes, especialistas e equipe interna.

## Tecnologias

- Python 3.12
- Django 6.1 e Django REST Framework 3.18
- PostgreSQL 15
- Simple JWT
- `django-filter`
- OpenAPI e Swagger UI com `drf-spectacular`
- Docker e Docker Compose
- Vue 3, Vite, Pinia e Vue Router
- Nginx para servir o frontend e encaminhar as chamadas da API

## Estrutura do projeto

```text
agendamentos/  Domínio de especialidades, agendas, horários e consultas
core/          Modelo-base, manager de registros ativos e exclusão lógica
frontend/      Aplicação Vue, estilos, painéis por perfil e configuração Nginx
setup/         Configurações, URLs e entrypoints ASGI/WSGI do Django
usuarios/      Usuário customizado e perfis de pacientes e especialistas
```

## Experiência no frontend

- Área pública com especialidades, profissionais e horários disponíveis.
- Login JWT com renovação automática do token de acesso.
- Paciente: filtra vagas, confirma uma reserva e acompanha suas consultas.
- Especialista: cria e desativa agendas, consulta vagas geradas e vê pacientes agendados.
- Interno ou superusuário: cadastra especialidades, credencia especialistas, cadastra pacientes e acompanha todas as consultas.
- Layout responsivo, estados de carregamento, mensagens de erro e confirmação de ações.

## Como executar com Docker

Pré-requisito: Docker com o comando `docker compose` disponível.

1. Crie o arquivo de ambiente:

```powershell
Copy-Item .env.example .env
```

No Linux ou macOS:

```bash
cp .env.example .env
```

2. Troque ao menos o valor de `SECRET_KEY` no arquivo `.env`.

3. Construa e inicie os serviços:

```bash
docker compose up --build
```

O serviço `web` aguarda o PostgreSQL ficar saudável, executa as migrations e disponibiliza a API em `http://127.0.0.1:8000/`. O frontend fica disponível em `http://127.0.0.1:5173/` e encaminha automaticamente as chamadas `/api/` para o backend.

Com os containers ativos, use:

```bash
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py test
docker compose exec web python manage.py spectacular --validate --fail-on-warn
```

Para encerrar:

```bash
docker compose down
```

`docker compose down -v` também remove definitivamente o volume local do PostgreSQL.

## Como executar localmente

Pré-requisitos: Python 3.12 e uma instância do PostgreSQL acessível.

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py test
python manage.py runserver
```

No Linux ou macOS, ative o ambiente com `source venv/bin/activate` e copie o arquivo com `cp .env.example .env`.

Antes de executar as migrations, ajuste as credenciais do PostgreSQL no `.env`. Fora do Docker, normalmente `POSTGRES_HOST=localhost`; no Compose esse valor é substituído por `db`.

Em outro terminal, inicie o frontend:

```powershell
cd frontend
npm install
npm run dev
```

Abra `http://127.0.0.1:5173/`. Durante o desenvolvimento, o Vite encaminha `/api/` para `http://127.0.0.1:8000/`, portanto não é necessária configuração adicional de CORS.

Para validar a versão de produção do frontend:

```powershell
cd frontend
npm run build
```

## Ambiente de produção

A aplicação está publicada no Render:

| Recurso | Endereço |
| --- | --- |
| Frontend Vue | [frontend-agendamentos-ixzf.onrender.com](https://frontend-agendamentos-ixzf.onrender.com/) |
| API Django | [api-agendamentos-ixzf.onrender.com/api](https://api-agendamentos-ixzf.onrender.com/api/) |
| Swagger UI | [api-agendamentos-ixzf.onrender.com/api/docs](https://api-agendamentos-ixzf.onrender.com/api/docs/) |
| Esquema OpenAPI | [api-agendamentos-ixzf.onrender.com/api/schema](https://api-agendamentos-ixzf.onrender.com/api/schema/) |

O frontend é um **Static Site** construído a partir do diretório `frontend/`.
Durante o build, a variável abaixo define a API consumida pelo Vue:

```text
VITE_API_URL=https://api-agendamentos-ixzf.onrender.com/api
```

O backend autoriza exclusivamente a origem publicada do frontend:

```text
CORS_ALLOWED_ORIGINS=https://frontend-agendamentos-ixzf.onrender.com
```

O arquivo `render.yaml` mantém a configuração do Static Site, incluindo o
rewrite de `/*` para `/index.html`. Esse rewrite permite acessar diretamente
rotas do Vue Router, como `/entrar` e `/painel`, sem receber erro 404.

A raiz `https://api-agendamentos-ixzf.onrender.com/` não possui uma página
própria; utilize o frontend para acessar o sistema ou `/api/docs/` para consultar
a documentação da API.

### Publicar uma atualização

1. Envie as alterações para a branch monitorada pelo serviço no Render.
2. O Static Site executará `npm ci && npm run build` e publicará `frontend/dist`.
3. Mudanças no backend exigem um novo deploy do serviço da API.
4. Se o domínio do frontend mudar, atualize `CORS_ALLOWED_ORIGINS` no backend.

## Variáveis de ambiente

| Variável | Finalidade | Valor de desenvolvimento |
| --- | --- | --- |
| `SECRET_KEY` | Chave criptográfica do Django | `troque-por-uma-chave-segura` |
| `DEBUG` | Ativa o modo de depuração | `True` |
| `ALLOWED_HOSTS` | Hosts permitidos, separados por vírgula | `localhost,127.0.0.1` |
| `CORS_ALLOWED_ORIGINS` | Origens do frontend autorizadas, separadas por vírgula | vazio |
| `TIME_ZONE` | Fuso horário da aplicação | `America/Sao_Paulo` |
| `POSTGRES_DB` | Nome do banco | `agendamentos_db` |
| `POSTGRES_USER` | Usuário do banco | `usuario_db` |
| `POSTGRES_PASSWORD` | Senha do banco | `senha123` |
| `POSTGRES_HOST` | Host do banco | `localhost` |
| `POSTGRES_PORT` | Porta do banco | `5432` |

Os valores do `.env.example` são apenas para desenvolvimento. Em produção, use uma chave forte, `DEBUG=False`, hosts explícitos e credenciais próprias.

## Autenticação e perfis

Obtenha e renove tokens JWT nestas rotas:

```http
POST /api/token/
POST /api/token/refresh/
```

Exemplo de autenticação:

```http
Authorization: Bearer <access_token>
```

O sistema possui três perfis: `PACIENTE`, `ESPECIALISTA` e `INTERNO`. Superusuários recebem as mesmas permissões administrativas de um usuário interno. Pacientes e especialistas são cadastrados por um usuário interno; não há endpoint público de autorregistro.

## Endpoints e permissões

Todos os endpoints de recurso terminam com `/`. As rotas de detalhe seguem o formato `/{id}/`.

| Método | Endpoint | Acesso |
| --- | --- | --- |
| `POST` | `/api/token/` | Público, com usuário e senha válidos |
| `POST` | `/api/token/refresh/` | Público, com refresh token válido |
| `GET` | `/api/usuarios/me/` | Usuário autenticado; retorna identidade e tipo de perfil |
| `GET` | `/api/usuarios/especialistas/` | Público |
| `POST`, `PUT`, `PATCH`, `DELETE` | `/api/usuarios/especialistas/` | Interno ou superusuário |
| CRUD | `/api/usuarios/pacientes/` | Interno ou superusuário |
| `GET` | `/api/agendamentos/especialidades/` | Público |
| `POST`, `PUT`, `PATCH`, `DELETE` | `/api/agendamentos/especialidades/` | Interno ou superusuário |
| CRUD | `/api/agendamentos/agendas/` | Especialista autenticado; somente as próprias agendas |
| `GET` | `/api/agendamentos/horarios/` | Público e somente leitura |
| `POST` | `/api/agendamentos/consultas/` | Paciente autenticado |
| `GET` | `/api/agendamentos/consultas/` | Paciente, especialista relacionado, interno ou superusuário |

Consultas aceitam apenas criação, listagem e detalhe: não podem ser alteradas nem excluídas pela API. Todas as listagens usam paginação de 20 itens.

### Exemplos de payload

Cadastrar uma especialidade:

```json
{"nome_especialidade": "Cardiologia"}
```

Cadastrar um especialista como usuário interno:

```json
{
  "usuario": {
    "username": "dra.ana",
    "password": "uma-senha-segura",
    "first_name": "Ana",
    "last_name": "Silva",
    "email": "ana@example.com",
    "cpf": "52998224725",
    "telefone": "11999998888"
  },
  "crm": "CRM-SP 123456",
  "especialidade": 1
}
```

O cadastro de paciente usa o mesmo objeto `usuario`, sem os campos `crm` e `especialidade`.

Criar uma agenda como especialista:

```json
{
  "dias_semana": 0,
  "hora_inicio_expediente": "08:00:00",
  "hora_fim_expediente": "12:00:00",
  "quantidade_vagas_dia": 4
}
```

`dias_semana` usa `0` para segunda-feira até `6` para domingo. O especialista é obtido do token e não deve ser enviado no payload.

Reservar um horário como paciente:

```json
{"horario_gerado": 1}
```

O paciente também é obtido do token.

### Filtros de horários

`GET /api/agendamentos/horarios/` aceita os filtros `status`, `data` e `agenda__especialista`:

```text
/api/agendamentos/horarios/?status=DISPONIVEL&data=2026-09-01&agenda__especialista=1
```

Os status possíveis são `DISPONIVEL` e `RESERVADO`.

## Regras de negócio

- Cada agenda pertence automaticamente ao especialista autenticado.
- Uma agenda define um dia da semana, início e fim do expediente e quantidade de vagas por dia.
- Na criação, são gerados horários para as ocorrências daquele dia da semana nos próximos 30 dias, incluindo o dia atual.
- O expediente é dividido igualmente pela quantidade de vagas; cada faixa precisa ter pelo menos um segundo.
- Um especialista não pode manter agendas com intervalos sobrepostos no mesmo dia da semana. Intervalos adjacentes são permitidos.
- Alterar a grade regenera os horários disponíveis. A grade não pode ser alterada quando já existem reservas.
- Não é possível reservar horários passados, inativos, pertencentes a agendas/especialistas inativos ou já reservados.
- Um paciente não pode ter consultas com horários sobrepostos.
- A reserva bloqueia as linhas do paciente e do horário em uma transação, evitando dupla reserva e conflitos concorrentes.
- Especialidades são únicas sem diferenciar maiúsculas de minúsculas; CPF, CRM e nome de usuário também são validados e normalizados.
- A exclusão é lógica. Desativar um perfil também desativa seu usuário; desativar uma agenda ou especialista desativa os horários relacionados.

## Documentação OpenAPI

Com a aplicação em execução:

- Swagger UI: `http://127.0.0.1:8000/api/docs/`
- Esquema OpenAPI: `http://127.0.0.1:8000/api/schema/`
- Administração Django: `http://127.0.0.1:8000/admin/`

Valide o esquema sem iniciar o servidor:

```bash
python manage.py spectacular --validate --fail-on-warn
```

## Testes

```bash
python manage.py test
```

A suíte cobre permissões, validações cadastrais, exclusão lógica, paginação, geração e regeneração de horários, consultas eficientes, conflitos de agenda, reservas sobrepostas e condições de corrida. Os testes de bloqueio concorrente dependem do PostgreSQL, pois usam `select_for_update`.
