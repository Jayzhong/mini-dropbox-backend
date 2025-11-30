# Architectural Decisions

## 1. Technology Stack
- **Language:** Python 3.12+
- **Dependency Manager:** `uv`
- **Web Framework:** FastAPI (Async)
- **ORM:** SQLAlchemy 2.0+ (Async)
- **Database:** PostgreSQL
- **Validation:** Pydantic V2 (Strict mode)
- **Blob Storage:** S3-compatible (MinIO for local dev)

## 2. Architecture Pattern
- **Style:** Domain-Driven Design (DDD) + Clean Architecture (Onion Architecture)
- **Layering:**
  1. **Domain (Innermost):** Pure Python entities and business logic. No frameworks.
  2. **Application:** Use cases, DTOs, interfaces for repositories/services.
  3. **Interfaces:** Adapters for the outside world (API routers, Repository implementations).
  4. **Infrastructure (Outermost):** DB config, models, S3 clients, framework wiring.

## 3. Key Constraints
- **Dependency Rule:** Dependencies point inwards only.
- **Entity vs. Model:** Explicit separation between Domain Entities (dataclasses) and DB Models (SQLAlchemy). Mappers are required.
- **Pydantic Usage:** restricted to the API layer (Request/Response schemas) only. Application layer uses pure Python dataclasses (DTOs).
- **Async First:** All I/O operations must be asynchronous.

## 4. Deployment (MVP)
- Single-process monolith.
- Local development uses `uvicorn` for the server and Docker (implied) or local services for Postgres/MinIO.
