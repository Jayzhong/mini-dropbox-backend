# Mini Dropbox Backend

A personal file storage service MVP (like a mini-Dropbox) built with a strict **Domain-Driven Design (DDD)** and **Clean Architecture** approach.

## 🚀 Tech Stack

- **Language**: Python 3.12+
- **Web Framework**: FastAPI (Async)
- **Database**: PostgreSQL (Async via `asyncpg`)
- **ORM**: SQLAlchemy 2.0
- **Object Storage**: MinIO (S3 Compatible)
- **Dependency Manager**: `uv`
- **Migrations**: Alembic
- **Containerization**: Docker & Docker Compose

## 🏗️ Architecture

This project adheres to the **Dependency Rule**: dependencies only point inwards.

```text
src/
├── domain/           # Enterprise Logic (Pure Python, No Frameworks)
├── application/      # Application Business Rules (Use Cases, DTOs)
├── interfaces/       # Interface Adapters (FastAPI Routers, Pydantic Schemas)
└── infrastructure/   # Frameworks & Drivers (SQLAlchemy, MinIO, Settings)
```

## ✨ Features

- **User Management**: Registration, Login, Authentication.
- **File System**:
  - Upload/Download files.
  - Create/List folders.
  - Hierarchical structure.
- **Sharing**:
  - Generate public read-only links.
  - Expiration support.
  - Disable/Revoke links.
- **Sync (Delta)**:
  - (In Progress) polling mechanism for changes.

## 🛠️ Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) & Docker Compose
- [uv](https://github.com/astral-sh/uv) (Python package manager)

### 1. Environment Setup

The project relies on environment variables. For local development, default values are provided in `src/infrastructure/config/settings.py`.

### 2. Start Infrastructure

Spin up PostgreSQL and MinIO:

```bash
docker-compose up -d
```

### 3. Install Dependencies

```bash
uv sync
```

### 4. Run Migrations

Apply database schema changes:

```bash
uv run alembic upgrade head
```

### 5. Run the Application

Start the FastAPI development server:

```bash
uv run fastapi dev src/interfaces/api/main.py
```

- **API**: `http://localhost:8000`
- **Docs**: `http://localhost:8000/docs`

### 6. Running Tests

Run the test suite (requires Docker infra running):

```bash
uv run pytest
```

## 📝 Development Rules

See [ARCHITECTURE_RULES.md](./ARCHITECTURE_RULES.md) for detailed coding guidelines regarding the DDD structure and strict separation of concerns.