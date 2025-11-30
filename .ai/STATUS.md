# Project Status & Context

**Last Updated:** November 30, 2025
**Current Agent:** Vibe Coding Agent (Mini-Dropbox Architect)

## 1. Current Phase: 🟢 Phase 3 Complete / Starting Phase 4
- **Completed:**
    - Phase 1: Foundation & Walking Skeleton (Deep Health Check).
    - Phase 2: User Management (Authentication & Registration).
    - Phase 3: User Management (Login & Session).
    - **Verification:** Robust Integration Test suite added for Auth endpoints (`tests/integration/test_auth.py`) and passing with transactional rollback per test.
- **In Progress:** None.
- **Next Up:** Phase 4: Core File Storage Functionality.

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
6.  **Testing Strategy:** Implemented transactional integration tests with FastAPI dependency override and `pytest-asyncio` for robust setup and teardown.

## 3. Immediate Next Steps (To-Do List)
- [ ] **Security Middleware:** Implement FastAPI Dependency for JWT authentication to protect routes.
- [ ] **User Context:** Create a mechanism to inject `current_user` into authenticated endpoints.
- [ ] **File Module - Database:** Define `FileModel` and `FolderModel` (SQLAlchemy). Generate Alembic migrations.
- [ ] **File Module - Domain:** Define `File` and `Folder` Entities, Value Objects (e.g., `StorageKey`), and Repository Interfaces.
- [ ] **File Module - Application:** Implement Use Cases for file upload, download, and listing.
- [ ] **File Module - Infrastructure:** Implement `MinIO` client integration for actual file storage.
- [ ] **File Module - API:** Create API endpoints for file and folder management.