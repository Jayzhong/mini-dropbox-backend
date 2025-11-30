# Coding Agent Guidelines: Python DDD & Clean Architecture

## 1. Project Overview & Philosophy

This project implements a backend system similar to Dropbox using **Python 3.12+**, **FastAPI**, and **SQLAlchemy 2.0 (Async)**.

The core architectural philosophy is **Domain-Driven Design (DDD)** combined with **Clean Architecture**. The primary goal is to decouple business logic from frameworks, databases, and external interfaces.

**⚠️ CRITICAL INSTRUCTION:** You must strictly adhere to the **Dependency Rule**: Source code dependencies can only point **inwards**.
- **Inner layers (Domain)** must NOT know about outer layers (Infra/API).
- **Outer layers (Infra)** depend on interfaces defined in inner layers.

## 2. Technical Stack & Tooling

- **Language:** Python 3.12+
- **Dependency Manager:** `uv` (Use `uv add`, `uv run`)
- **Web Framework:** FastAPI (Async)
- **ORM:** SQLAlchemy 2.0+ (Async, `Mapped[]`, declarative base)
- **Migrations:** Alembic (Async configuration)
- **Validation:** Pydantic V2 (Strict mode)
- **Database:** PostgreSQL (Async driver: `asyncpg`)
- **Linter/Formatter:** Ruff
- **Testing:** Pytest + Pytest-Asyncio

## 3. Directory Structure & Layer Responsibilities

The project root is `src/`. STRICTLY follow this structure. Note the placement of Repository Implementations in Infrastructure.

```text
src/
├── domain/                         # LAYER 1 (Innermost): Enterprise Logic
│   ├── common/                     # Shared Value Objects, Base Entities
│   ├── user/                       # Aggregate: User
│   │   ├── entity.py               # Pure Python Data Classes
│   │   ├── exceptions.py           # Domain Exceptions
│   │   └── values.py               # Value Objects (e.g., UserID, Email)
│   └── ...
│
├── application/                    # LAYER 2: Application Logic / Use Cases
│   ├── common/                     # Interfaces (UoW Protocol, DTO base)
│   │   ├── interfaces.py           # Abstract Repo Definitions defined here or in domain
│   ├── user/
│   │   ├── dto.py                  # Input/Output DTOs (Pure dataclasses)
│   │   └── use_cases.py            # Application Services / Interactors
│   └── ...
│
├── interfaces/                     # LAYER 3: Interface Adapters (Entry Points)
│   ├── api/                        # Driving Adapters (Web)
│   │   ├── v1/
│   │   │   ├── routers/            # FastAPI Routes
│   │   │   └── schemas/            # Pydantic Models (HTTP Request/Response)
│   │   └── dependencies.py         # DI wiring (Entry point for composition)
│
└── infrastructure/                 # LAYER 4 (Outermost): Frameworks & Drivers
    ├── config/                     # Settings (pydantic-settings)
    ├── database/
    │   ├── main.py                 # Async Engine & Session Factory
    │   ├── migrations/             # Alembic versions
    │   └── models/                 # SQLAlchemy ORM Models
    ├── repositories/               # Driven Adapters (Implementation)
    │   └── user.py                 # SQLAlchemy implementation of UserRepository
    └── services/                   # External services (S3, Email, Redis)
```

## 4. Strict Development Rules

### Rule #1: The "No Frameworks in Domain" Rule

- **Domain Layer (`src/domain`)**: Must NOT import `fastapi`, `sqlalchemy`, `pydantic`, or `alembic`.
    
- It should contain only standard Python libraries.
    
- **Reason**: The core business logic must remain pure and testable without external IO.
    

### Rule #2: Entity vs. Model Separation

- **Entities (`domain`)**: Pure Python `dataclasses` defining business behavior and state.
    
- **Models (`infrastructure`)**: SQLAlchemy classes (`Base`) defining database tables.
    
- **The Mapping**: You must write explicit mappers in the **Infrastructure Repository** to convert:
    
    - `Model -> Entity` (when reading from DB)
        
    - `Entity -> Model` (when saving to DB)
        
- **Forbidden**: Never pass an SQLAlchemy Model to the Use Case or API layer.
    

### Rule #3: Pydantic Isolation

- **Pydantic Models**: Allowed **ONLY** in `src/interfaces/api/schemas` (for HTTP validation) or `src/infrastructure/config` (for settings).
    
- **Application DTOs**: The Application layer must use standard Python `@dataclass`.
    
- **Reason**: Pydantic is an I/O boundary tool. Domain logic should not depend on validation libraries.
    

### Rule #4: Dependency Injection & Inversion

- **Abstracts**: Define Repository/Service interfaces (Protocols/ABCs) in `src/application` or `src/domain`.
    
- **Concretions**: Implement them in `src/infrastructure`.
    
- **Wiring**: Use FastAPI `Depends` in `src/interfaces/api/dependencies.py` to inject implementations into Use Cases.
    
- **Forbidden**: Do not instantiate `SQLAlchemyUserRepository` directly inside a Use Case.
    

### Rule #5: Database & Transaction Management

- **Async Only**: Use `AsyncSession` and `select()`, `insert()`, `update()`, `delete()` syntax.
    
- **Unit of Work (UoW)**: Implement a UoW pattern to manage transactions.
    
    - Commits should happen in the **Application Layer** (Use Case) via UoW, NOT in the Repository.
        
    - Repositories should only `add`, `flush`, or `execute`.
        

## 5. Database Management (Alembic)

- **Configuration**: Use `alembic` with an **async** `env.py` configuration (using `run_migrations_online` with `connectable`).
    
- **Workflow**:
    
    1. Modify `infrastructure/database/models/*.py`.
        
    2. Ensure all models are imported in `infrastructure/database/main.py` or Alembic's `env.py` (target metadata).
        
    3. Run: `uv run alembic revision --autogenerate -m "describe_change"`.
        
    4. Run: `uv run alembic upgrade head`.
        
- **Naming**: Migration files must use the format `{revision_id}_{slug}.py`.
    
- **Constraint**: DO NOT use `create_all()`. All schema changes must go through Alembic.
    

## 6. Naming Conventions

|**Concept**|**Suffix/Style**|**Example**|**Location**|
|---|---|---|---|
|**Domain Entity**|PascalCase|`User`|`src/domain/user/entity.py`|
|**DB Model**|`Model` suffix|`UserModel`|`src/infra/database/models/user.py`|
|**Pydantic Schema**|`Request`/`Response`|`CreateUserRequest`|`src/interfaces/api/schemas/`|
|**App DTO**|`DTO` suffix|`CreateUserInputDTO`|`src/application/user/dto.py`|
|**Repo Interface**|`Repository`|`UserRepository` (Protocol)|`src/application/common/interfaces/`|
|**Repo Impl**|`SqlAlchemy...`|`SqlAlchemyUserRepository`|`src/infrastructure/repositories/`|

## 7. Error Handling Strategy

1. **Domain Layer**: Raise pure Python custom exceptions (e.g., `UserNotFound`, `InsufficientFunds`).
    
2. **Application Layer**: Catch technical errors, wrap in App exceptions if needed, or let Domain exceptions bubble up.
    
3. **Interface Layer (API)**: Use a global `exception_handler` in `src/interfaces/api/main.py`.
    
    - Map `UserNotFound` (Domain) -> HTTP 404.
        
    - Map `PermissionError` (Domain) -> HTTP 403.
        
    - **Never** return HTTP responses (JSONResponse) directly from Use Cases.
        

## 8. Development Workflow (UV & Ruff)

- **Dependencies**:
    
    - `uv add fastapi uvicorn[standard] sqlalchemy asyncpg pydantic-settings alembic`
        
    - `uv add --dev ruff pytest pytest-asyncio`
        
- **Linting**: Run `uv run ruff check .` before committing.
    
- **Testing Strategy**:
    
    - **Unit Tests**: Test Domain Entities and Use Cases using mocks. No DB access.
        
    - **Integration Tests**: Test Infrastructure Repositories using a real test DB (spin up via Docker).
        