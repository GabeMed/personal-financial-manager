> English version and quick start: [README.md](../README.md)

## Finance Manager – Documentação Técnica

### Conteúdo

1. #### Visão Geral
2. #### Arquitetura

   * Backend (FastAPI + Clean Architecture)
   * Frontend (React + Lean Architecture)
3. #### Estrutura de Diretórios
4. #### Tecnologias e Bibliotecas
5. #### Configuração & Execução
6. #### Variáveis de Ambiente
7. #### API Endpoints Principais
8. #### Design Patterns & Boas Práticas
9. #### Testes
10. #### Requisitos Ausentes
---

## Visão Geral

Aplicação SPA para gestão financeira pessoal, com autenticação JWT, CRUD de categorias e transações, e dashboard com saldo e gráficos de despesas por categoria.

---

## Arquitetura

### Backend

* **Clean Architecture** dividida em:

  * **Core**: configurações (env/settings), segurança (hash de senha, OAuth2/JWT).
  * **DB**: SQLAlchemy + SessionLocal/Base; tabelas criadas via `Base.metadata.create_all()` no startup (sem migrações ainda).
  * **Models**: entidades `User`, `Category`, `Transaction` (com enums e relacionamentos).
  * **Schemas**: Pydantic v2 DTOs separados em Create/Read/Update.
  * **CRUD**: repositórios em `app/crud/`.
  * **Services**: lógica de negócio em `app/services/`; erros de negócio (`NotFoundError`, `ConflictError`) são convertidos em HTTP 404/409 em `main.py`.
  * **API**: routers versionados em `app/api/v1/`, protegidos pelo dependency `get_current_user`.

### Frontend

* **Lean Architecture** com pastas claras:

  * **`/context`**: `AuthContext` (login, logout, user).
  * **`/hooks`**: React Query para dados (`useCategories`, `useTransactions`, `useSummary`, `useCreateCategory`, `useCreateTransaction`, `useUpdateTransaction`, `useDeleteTransaction`).
  * **`/components`**: UI atômica com Chakra UI v3 (`Dialog`, `Field`, `Button`, etc.), formulários e gráficos (`PieChartCard`).
  * **`/pages`**: rotas protegidas (`DashboardPage`).
  * **`/services/apiClient.ts`**: instância Axios com interceptor JWT.
  * **`/types`**: DTOs TypeScript gerados manualmente.
  * **`/schemas`**: Zod para validação de payloads de formulário.

---

## Estrutura de Diretórios

```text
backend/                    # FastAPI app
├─ app/
│  ├─ core/                 # settings, segurança
│  ├─ db/                   # SQLAlchemy Base & Session
│  ├─ models/               # ORM models
│  ├─ schemas/              # Pydantic DTOs
│  ├─ crud/                 # repositórios DB
│  ├─ services/             # lógica de negócio
│  ├─ api/
│  │  └─ v1/                # routers (auth, categories, transactions, summary)
│  └─ seed.py               # dados de demonstração (demo / demo1234)
├─ tests/                   # pytest
frontend/                   # React + TS
├─ src/
│  ├─ context/              # AuthContext.tsx
│  ├─ hooks/                # useCategories.ts, useTransactions.ts, useSummary.ts, etc.
│  ├─ components/           # PieChartCard, TransactionList, TransactionForm ...
│  ├─ pages/                # DashboardPage.tsx, LoginPage.tsx, RegistrationPage.tsx
│  ├─ services/             # apiClient.ts, authClient.ts ...
│  ├─ types/                # CategoryDTO, TransactionDTO, SummaryDTO
│  └─ schemas/              # NewTransactionSchema, NewCategorySchema
```

---

## Tecnologias e Bibliotecas

* **Backend**: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2, Uvicorn, PostgreSQL (ou SQLite)
* **Frontend**: React 19, TypeScript, Vite, Chakra UI v3, React Query v5, React Router v7, Zod, React Hook Form, Recharts
* **Autenticação**: OAuth2 Password + JWT Bearer

---

## Configuração & Execução

### Clone o repositório
```bash
git clone https://github.com/GabeMed/personal-financial-manager.git
# entre no diretório
cd personal-financial-manager
```

### Com Docker (recomendado)

```bash
docker compose up --build
# app: http://localhost:5173 (login: demo / demo1234) · API: http://localhost:8000/docs
```

### Backend

```bash
# criar e ativar venv
python -m venv .venv && source .venv/bin/activate
# instalar deps
cd backend
pip install -r requirements.txt
# rodar o backend
cd ..
uvicorn backend.app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
cd finance-app
# instalar deps
npm install
# rodar
npm run dev
```

---

## Variáveis de Ambiente

| Nome                  | Descrição                     | Exemplo                             |
| --------------------- | ----------------------------- | ----------------------------------- |
| `DATABASE_URL`        | URL do banco (SQLAlchemy)     | `sqlite:///./app.db` (padrão) ou `postgresql+psycopg://...` |
| `SECRET_KEY`          | Chave JWT                     | `yourSecret.`                       |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Validade do token (minutos) | `30`                          |
| `CORS_ORIGINS`        | Origens permitidas (vírgula)  | `http://localhost:5173`             |
| `SEED_DEMO_DATA`      | Cria o usuário demo no startup| `true`                              |
| `VITE_API_URL`        | Base URL do backend no front  | `http://localhost:8000/api/v1`      |

---

## API Endpoints Principais

| Método | Rota                           | Descrição                                    |
| ------ | ------------------------------ | -------------------------------------------- |
| POST   | `/api/v1/users/register`       | Cadastro                                     |
| POST   | `/api/v1/auth/token`           | Login, retorna JWT                           |
| GET    | `/api/v1/users/me`             | Dados do usuário logado                      |
| GET    | `/api/v1/categories/all`       | Listar categorias do usuário                 |
| POST   | `/api/v1/categories`           | Criar categoria                              |
| GET    | `/api/v1/transactions/all`     | Listar transações                            |
| POST   | `/api/v1/transactions`         | Criar transação                              |
| PATCH  | `/api/v1/transactions/{id}`    | Editar transação                             |
| DELETE | `/api/v1/transactions/{id}`    | Excluir transação                            |
| GET    | `/api/v1/transactions/summary` | Resumo (balance, income/expense totals & %s) |

---

## Design Patterns & Boas Práticas

* **Clean Architecture** (backend): separação clara entre camadas
* **React Hooks** para composição de lógica de dados (React Query)
* **Validação em Runtime** com Zod + `react-hook-form`
* **JWT + Axios Interceptor** para autenticação automática

---

## Testes

```bash
cd backend
pip install -r requirements-dev.txt
pytest                      # SQLite em memória
TEST_DATABASE_URL=postgresql+psycopg://user:pass@localhost/db pytest   # PostgreSQL
```

38 testes cobrindo autenticação, categorias (duplicadas, nome inválido, isolamento entre usuários), transações (criar, atualizar, excluir, impacto no saldo, validação) e o resumo (`/transactions/summary`: totais, percentuais e filtro por data). O CI roda ruff + pytest (SQLite e PostgreSQL), lint + build do frontend e um smoke test do `docker compose`.

---

## Requisitos Ausentes

### Filtragem Básica

#### Backend

* **GET `/transactions`**

  * parâmetros opcionais de query:

    * `start_date` (YYYY-MM-DD)
    * `end_date` (YYYY-MM-DD)
    * `category_id` (inteiro)
  * aplicar filtros no repositório:

    ex:
    ```python
    query = db.query(Transaction).filter(Transaction.user_id == user.id)
    if start_date: query = query.filter(Transaction.date >= start_date)
    if end_date:   query = query.filter(Transaction.date <= end_date)
    if category_id: query = query.filter(Transaction.category_id == category_id)
    ```
  * retornar lista filtrada

## Motivação das Prioridades

* **Charts em vez de filtros**: um dashboard visual (saldo + gráfico de pizza) dá **insight imediato** sobre os padrões de gastos, acelerando a validação do MVP. Filtros são importantes, mas geram menos “wow” inicial e podem ficar para iteração seguinte.
* **Teste automatizado deixado para depois**: foquei primeiro na **entrega de valor visível** (autenticação, CRUD, dashboard reativo). Com a base de funcionalidades estável, os testes foram adicionados depois (ver seção Testes).

