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

Você pode executar o projeto de duas formas: utilizando **Docker (Recomendado)** ou rodando localmente (Virtualenv).

### Opção A: Rodando com Docker (Recomendado)
A forma mais fácil de rodar o projeto e o banco de dados sem instalar dependências extras na sua máquina.

1. **Subir os contêineres:**
```bash
docker-compose up -d
```
2. **Rodar as migrações (se for a primeira vez):**
```bash
docker-compose exec web python manage.py migrate
```
3. **Criar um superusuário (Painel Admin e permissões Internas):**
```bash
docker-compose exec web python manage.py createsuperuser
```
4. **Executar os testes automatizados:**
```bash
docker-compose exec web python manage.py test
```
A API estará rodando em `http://127.0.0.1:8000/`.

---

### Opção B: Rodando Localmente (Virtualenv)

**1. Clonar e Configurar o Ambiente Virtual**
```bash
python -m venv venv
# Ativar no Windows:
venv\Scripts\activate
# Ativar no Linux/Mac:
source venv/bin/activate
```

**2. Instalar Dependências**
```bash
pip install -r requirements.txt
```

**3. Configurar Variáveis de Ambiente (.env)**
Crie um arquivo `.env` na raiz do projeto e aponte para um banco PostgreSQL local:
```env
SECRET_KEY=sua_chave_secreta_super_segura
DEBUG=True
POSTGRES_DB=agendamentos_db
POSTGRES_USER=usuario_db
POSTGRES_PASSWORD=senha123
POSTGRES_HOST=localhost
```

**4. Migrar, Testar e Iniciar**
```bash
python manage.py migrate
python manage.py test
python manage.py runserver
```

---

## 📖 Documentação Automática (Swagger)

A API é auto-documentada. Com o servidor rodando, acesse:
- **Interface Interativa (Swagger):** `http://127.0.0.1:8000/api/docs/`
- **Esquema OpenAPI:** `http://127.0.0.1:8000/api/schema/`

---

## 🗺️ Mapeamento de Rotas (Endpoints) e Permissões

O sistema possui um controle rígido de perfis (RBAC). A maioria das rotas exige um Token JWT no cabeçalho (`Authorization: Bearer <token>`).

### 🔐 Autenticação (JWT)
- `POST /api/token/` - Gera token de acesso (`access`) e atualização (`refresh`).
- `POST /api/token/refresh/` - Atualiza o token expirado.

### 👤 Usuários (Uso Interno)
*Endpoints destinados ao credenciamento. Apenas usuários `INTERNO` ou `Administradores` podem criar, editar ou excluir. Leitura (GET) liberada.*
- `GET | POST | PUT | PATCH | DELETE /api/usuarios/especialistas/` - (Soft Delete habilitado).
- `GET | POST | PUT | PATCH | DELETE /api/usuarios/pacientes/` - (Soft Delete habilitado).

### 📅 Agendamentos (Regras de Negócio)
- `GET | POST | PUT | PATCH | DELETE /api/agendamentos/especialidades/` - **Apenas nível `INTERNO`** cria/edita. Leitura liberada.
- `GET | POST | PUT | PATCH | DELETE /api/agendamentos/agendas/` - **Exige perfil `ESPECIALISTA`.** Listagem bloqueada para mostrar apenas as agendas do médico logado. A criação da agenda aciona um **Signal** no banco de dados que gera **automaticamente** os horários vagos (slots).
- `GET /api/agendamentos/horarios/` - Lista os horários gerados no sistema. 
  - 🔍 *Filtros Dinâmicos:* `/api/agendamentos/horarios/?status=DISPONIVEL&data=2024-11-01`
- `GET | POST | PUT | PATCH | DELETE /api/agendamentos/consultas/` - **Exige perfil `PACIENTE`.** Listagem restrita às próprias consultas. O endpoint é travado contra Race Conditions via `select_for_update()`, impedindo agendamentos duplos.

---
> 💡 *Nota Arquitetural: O projeto utiliza `ActiveManager` para omitir automaticamente entidades com "Soft Delete" (`is_active=False`) de todas as querys, e captura validações nativas do Django repassando-as como HTTP 400 Bad Request via DRF.*

