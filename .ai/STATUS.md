# Project Status & Context

**Last Updated:** November 30, 2025
**Current Agent:** Vibe Coding Agent (Mini-Dropbox Architect)

## 1. Current Phase: 🟢 Phase 1 Complete / Starting Phase 2
- **Completed:** Phase 1: Foundation & Walking Skeleton (Deep Health Check).
- **In Progress:** None.
- **Next Up:** Phase 2: User Management (Authentication & Registration).

## 2. Key Architectural Decisions (Immutable)
1.  **The Dependency Rule:** Source code dependencies MUST flow inwards. Domain depends on nothing.
2.  **No Frameworks in Domain:** `src/domain` is pure Python. No Pydantic, SQLAlchemy, or FastAPI imports.
3.  **Layer Responsibilities:**
    - **Domain:** Enterprise logic, Entities (dataclasses), Custom Exceptions.
    - **Application:** Use Cases, DTOs, Repository Interfaces (Protocols).
    - **Interface:** HTTP Routers, Pydantic Schemas (IO only).
    - **Infrastructure:** DB Models, Repository Implementations, External Adapters.
4.  **Async Stack:**
    - **Web:** FastAPI (Async).
    - **DB:** PostgreSQL + `asyncpg` + SQLAlchemy 2.0 (AsyncSession).
    - **Fix:** `greenlet` added to support SQLAlchemy async operations.
5.  **Infrastructure:**
    - Docker Compose running Postgres, MinIO (S3), and Redis.
    - `S3_ENDPOINT_URL` configured for local MinIO.

## 3. Immediate Next Steps (To-Do List)
- [ ] **User Module - Database:** Create `UserModel` (SQLAlchemy) and generate Alembic migration.
- [ ] **User Module - Domain:** Define `User` Entity and Repository Interface.
- [ ] **User Module - Feature:** Implement `RegisterUserUseCase` (hashing passwords).
- [ ] **User Module - API:** Create `POST /api/v1/auth/register` endpoint.
- [ ] **User Module - Security:** Implement Login & JWT Token generation.
