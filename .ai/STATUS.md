# Project Status & Context

**Last Updated:** November 30, 2025
**Current Agent:** Vibe Coding Agent (Mini-Dropbox Architect)

## 1. Current Phase: 🟢 Phase 2 Complete / Starting Phase 3
- **Completed:**
    - Phase 1: Foundation & Walking Skeleton (Deep Health Check).
    - Phase 2: User Management (Authentication & Registration).
    - **Verification:** Integration Tests added (`tests/integration/test_auth.py`) and passing.
- **In Progress:** None.
- **Next Up:** Phase 3: User Management (Login & Session).

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
    - **Auth:** Switched to `Argon2` (via `argon2-cffi`) for robust password hashing.
    - **Transaction:** Explicit `UnitOfWork` pattern implemented for Use Case commits.
5.  **Infrastructure:**
    - Docker Compose running Postgres, MinIO (S3), and Redis.
    - `S3_ENDPOINT_URL` configured for local MinIO.

## 3. Immediate Next Steps (To-Do List)
- [ ] **User Login - Feature:** Implement `LoginUserUseCase` (verify password, generate token).
- [ ] **User Login - API:** Create `POST /api/v1/auth/login` endpoint.
- [ ] **Security:** Introduce JWT or session management (depending on decision during implementation).
