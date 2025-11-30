# MVP Task List

## Phase 1: Foundation & Authentication
- [ ] **Project Setup**: Initialize `pyproject.toml` with `uv`, set up `src` structure, configure `uvicorn`.
- [ ] **Infrastructure Setup**: Configure SQLAlchemy async engine, session factory, and base model.
- [ ] **User Domain**: Define `User` entity and `UserRepository` interface.
- [ ] **User Infrastructure**: Implement `SQLAlchemyUserRepository` and `UserModel`.
- [ ] **Auth Use Cases**: Implement `RegisterUser` and `Login` (JWT generation).
- [ ] **Auth API**: Create `/auth/register` and `/auth/login` endpoints with Pydantic schemas.

## Phase 2: Folder Management (Metadata)
- [ ] **Folder Domain**: Define `Folder` entity and logic (e.g., no duplicate names in same parent).
- [ ] **Folder Infrastructure**: Implement `FolderModel` and `SQLAlchemyFolderRepository`.
- [ ] **Folder Use Cases**: `CreateFolder`, `ListFolderContents` (files & folders).
- [ ] **Folder API**: Create endpoints for creating and listing folders.

## Phase 3: File Management (Core)
- [ ] **File Domain**: Define `File` entity.
- [ ] **Blob Storage Interface**: Define `BlobStorageService` protocol.
- [ ] **Blob Storage Infrastructure**: Implement `MinioBlobStorageService` (or LocalFS fallback for initial dev).
- [ ] **File Infrastructure**: Implement `FileModel` and `SQLAlchemyFileRepository`.
- [ ] **File Use Cases**: `UploadFile` (metadata + blob put), `DownloadFile` (blob get).
- [ ] **File API**: endpoints for upload/download.

## Phase 4: Sharing
- [ ] **Share Domain**: Define `ShareLink` entity and token generation logic.
- [ ] **Share Infrastructure**: Implement `ShareLinkModel` and repo.
- [ ] **Share Use Cases**: `CreateShareLink`, `RevokeShareLink`, `AccessSharedFile`.
- [ ] **Share API**: Public endpoint for downloading via token.

## Phase 5: Sync (Delta API)
- [ ] **Sync Domain**: Define `ChangeLog` entity.
- [ ] **Sync Infrastructure**: Implement `ChangeLogModel` and hooking mechanism (or explicit calls) to record changes.
- [ ] **Sync Use Case**: `GetDeltas` (fetch changes since cursor).
- [ ] **Sync API**: `GET /delta` endpoint.
