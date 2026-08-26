# API de Agendamentos Médicos

Este é o backend de um sistema de agendamentos médicos, desenvolvido como parte de um teste técnico utilizando **Django** e **Django REST Framework (DRF)**.

O sistema permite a gestão de especialidades, especialistas, pacientes, agendas (com geração automática de horários baseada no expediente) e a marcação de consultas médicas garantindo o controle de concorrência (*Race Condition*).

## 🚀 Tecnologias Utilizadas

- **Linguagem:** Python 3
- **Framework:** Django 6.1, Django REST Framework
- **Banco de Dados:** PostgreSQL
- **Autenticação:** JWT (JSON Web Tokens) via `djangorestframework-simplejwt`
- **Filtros e Paginação:** `django-filter` e paginação nativa do DRF
- **Documentação:** Swagger UI via `drf-spectacular`

---

## 🛠️ Instruções Claras para Execução do Projeto

Siga os passos abaixo para rodar o projeto localmente:

### 1. Pré-requisitos
Certifique-se de ter instalado em sua máquina:
- Python 3.10+
- PostgreSQL rodando localmente (ou via Docker)

### 2. Clonar e Configurar o Ambiente Virtual
No terminal, na pasta do projeto, crie e ative o ambiente virtual:
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar no Windows:
venv\Scripts\activate

# Ativar no Linux/Mac:
source venv/bin/activate
```

### 3. Instalar Dependências
Com o ambiente ativado, instale os pacotes necessários:
```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente (.env)
Crie um arquivo `.env` na raiz do projeto (mesmo nível do `manage.py`) com as configurações do seu banco de dados e do Django:
```env
SECRET_KEY=sua_chave_secreta_super_segura
DEBUG=True
POSTGRES_DB=agendamentos_db
POSTGRES_USER=usuario_db
POSTGRES_PASSWORD=senha123
POSTGRES_HOST=localhost
```

### 5. Configurar o Banco de Dados
Certifique-se de que o banco de dados PostgreSQL especificado no `.env` está criado. Em seguida, rode as migrações:
```bash
python manage.py migrate
```

*(Opcional)* Crie um superusuário para acessar o painel administrativo:
```bash
python manage.py createsuperuser
```

### 6. Executar o Servidor
Inicie o servidor de desenvolvimento:
```bash
python manage.py runserver
```
A API estará rodando em `http://127.0.0.1:8000/`.

### 7. Executar os Testes Automatizados
O projeto conta com testes robustos (incluindo simulação de *Race Condition* com threads e bloqueio de DB). Para rodá-los:
```bash
python manage.py test
```

---

## 📖 Documentação Automática (Swagger)

A API é auto-documentada. Com o servidor rodando, você pode testar e ver os detalhes dos payloads acessando o painel do Swagger:
- **Interface Interativa (Swagger):** `http://127.0.0.1:8000/api/docs/`
- **Esquema OpenAPI:** `http://127.0.0.1:8000/api/schema/`

---

## 🗺️ Mapeamento de Rotas (Endpoints)

Abaixo estão listadas todas as rotas mapeadas pela API. A maioria exige um Token JWT no cabeçalho de requisição (`Authorization: Bearer <token>`).

### 🔐 Autenticação (JWT)
*Gerenciamento de acesso dos usuários à plataforma.*
- `POST /api/token/` - Gera um token de acesso (`access`) e atualização (`refresh`) ao enviar usuário e senha.
- `POST /api/token/refresh/` - Atualiza o token de acesso que expirou usando o token de refresh.

### 👤 Usuários
*Gestão de perfis da aplicação.*
- `GET | POST | PUT | PATCH | DELETE /api/usuarios/especialistas/` - CRUD de médicos/especialistas. (O *delete* executa um Soft Delete, desativando também a conta associada).
- `GET | POST | PUT | PATCH | DELETE /api/usuarios/pacientes/` - CRUD de pacientes.

### 📅 Agendamentos
*O Core Business do sistema de marcações.*
- `GET | POST | PUT | PATCH | DELETE /api/agendamentos/especialidades/` - Cadastro de áreas médicas (ex: Cardiologia, Pediatria).
- `GET | POST | PUT | PATCH | DELETE /api/agendamentos/agendas/` - **Requer Especialista logado.** A criação de uma agenda gera **automaticamente** os horários vagos do médico no banco de dados, baseado no horário de início/fim e vagas diárias.
- `GET | POST | PUT | PATCH | DELETE /api/agendamentos/horarios/` - Lista os horários (slots) gerados no sistema. 
  - 🔍 **Suporta Filtros Dinâmicos:** Ex: `/api/agendamentos/horarios/?status=DISPONIVEL&data=2024-11-01`
- `GET | POST | PUT | PATCH | DELETE /api/agendamentos/consultas/` - **Requer Paciente logado.** Realiza a reserva de um `HorarioGerado`. Bloqueado contra agendamentos simultâneos para a mesma vaga (*Transaction Lock*).

---
> 💡 *Nota: A paginação global está habilitada. Todas as rotas de listagem (GETs em coleções) retornarão os dados paginados com o tamanho de 20 itens por página (configurável no settings).*

