# Project Status & Context

**Last Updated:** December 1, 2025
**Current Agent:** Lead Backend Architect (Codex)

## 1. Current Phase: 🟢 Phase 4 In Progress (Core File Storage)
- **Completed:**
    - Phase 1: Foundation & Walking Skeleton (Deep Health Check).
    - Phase 2: User Management (Authentication & Registration).
    - Phase 3: User Management (Login & Session).
    - **Verification:** Integration suite expanded (files, folders, share links) and passing.
- **In Progress:** File storage + sharing (ShareLink) build-out.
- **Next Up:** Continue Phase 4: Core File Storage Functionality.

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

- [ ] **Security Middleware:** Implement FastAPI dependency/middleware for JWT-protected routes; ensure `current_user` injection is used across endpoints. (Router-level guards in place; consider middleware/global guard.)
- [ ] **User Context:** Centralize and reuse `current_user` dependency across new routes (cache added on request.state).
- [ ] **File Module - Domain:** Finish value objects (e.g., StorageKey, FileName) and validations; add domain exceptions for conflicts/soft deletes.
- [ ] **File Module - Database:** Confirm `FileModel`/`FolderModel` schemas; keep Alembic head synced (share_links migration applied).
- [ ] **File Module - Application:** Expand use cases with soft delete, size/mime validation, delta/sync groundwork.
- [ ] **File Module - Infrastructure:** Harden MinIO integration (structured logging, retries/backoff, content-length handling, configurable presign TTL).
- [ ] **Share Links - API:** Add owner listing of share links per file; consider returning presigned URL in body alongside redirect.
- [ ] **Testing:** Add unit tests for share-link use cases (expiry/disable/token); add negative cases for unauthorized access to share-link disable; keep integration suite updated.
