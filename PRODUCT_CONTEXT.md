# PRODUCT_CONTEXT: Personal File Storage MVP

## 1. Product Scope

### 1.1 Goal

Build a small, Dropbox-like **personal file storage MVP** that runs as a **single-process monolithic application** on one machine.

The system is for **individual users** (no teams / organizations) and supports:

- Uploading and downloading files.
- Basic folder hierarchy.
- Read-only share links with expiration.
- A simple "delta" mechanism to help clients sync changes.

The system only needs **eventual consistency**; we do not need strict transactional behavior between metadata and file blobs.

---

### 1.2 In-Scope Features (MVP)

1. **Authentication**

   - User registration: email + password.
   - User login: returns some form of token or session (implementation detail left to the code).

2. **Folders**

   - Create folder under a parent folder.
   - List folders and files under a folder.
   - Soft delete folder (optional for first iteration; can be a `deleted_at` flag).

3. **Files**

   - Upload a file to a specific folder.
   - Download a file by its ID.
   - List files in a folder (mixed with folders in the same call is okay).
   - Soft delete file (mark as deleted, hide it from listing).

4. **Share Links (Read-Only)**

   - Generate a public, read-only share link for a single file, with:
     - Random token.
     - Optional expiration time.
   - Public access should validate:
     - Token existence.
     - Expiration.
     - Disabled flag.
   - Ability to disable a share link (e.g., `is_disabled = true`).

5. **Basic Sync / Delta Mechanism**

   - A simple mechanism that returns **changes since a cursor** for one user:
     - Files created/updated/deleted.
     - Folders created/updated/deleted.
   - Clients poll this mechanism periodically to keep themselves in sync.
   - Conflict resolution: **last write wins** on the server.

---

### 1.3 Out of Scope (for this MVP)

- Team/organization features, group permissions, or multi-tenant ACL.
- Chunked uploads, resumable uploads, and content-based deduplication.
- Real-time collaborative editing.
- Multi-region deployment, CDN integration, and advanced scaling topics.
- Advanced security (KMS, end-to-end encryption, etc.).

---

## 2. Core Data Models

The following entities should be enough for the implementation to design tables / models.

Types below are conceptual; the concrete types depend on the chosen language/ORM.

---

### 2.1 User

Represents a single end user.

| Field         | Type          | Notes                          |
|---------------|---------------|--------------------------------|
| id            | UUID / BIGINT | Primary key                    |
| email         | STRING        | Unique                         |
| password_hash | STRING        | Hashed password                |
| created_at    | TIMESTAMP     |                                |
| updated_at    | TIMESTAMP     |                                |

---

### 2.2 Folder

Represents a folder in a user's personal namespace.

| Field      | Type          | Notes                                                       |
|------------|---------------|-------------------------------------------------------------|
| id         | UUID / BIGINT | Primary key                                                 |
| user_id    | FK(User)      | Owner                                                       |
| name       | STRING        | Folder name                                                 |
| parent_id  | FK(Folder)    | Nullable; `NULL` means top-level folder                     |
| created_at | TIMESTAMP     |                                                             |
| updated_at | TIMESTAMP     |                                                             |
| deleted_at | TIMESTAMP     | Nullable; soft delete                                       |

Constraint (recommended):

- `(user_id, parent_id, name)` is unique among non-deleted rows.

---

### 2.3 File

Represents a logical file.

| Field       | Type          | Notes                                             |
|-------------|---------------|---------------------------------------------------|
| id          | UUID / BIGINT | Primary key                                       |
| user_id     | FK(User)      | Owner                                             |
| folder_id   | FK(Folder)    | Parent folder                                    |
| name        | STRING        | File name shown to the user                      |
| size_bytes  | BIGINT        | File size in bytes                               |
| mime_type   | STRING        | Best-effort MIME type                            |
| storage_key | STRING        | Key used in blob storage (e.g., S3, MinIO, etc.) |
| created_at  | TIMESTAMP     |                                                   |
| updated_at  | TIMESTAMP     |                                                   |
| deleted_at  | TIMESTAMP     | Nullable; soft delete                             |

For this MVP we only store the latest version; version history is out of scope.

---

### 2.4 ShareLink

Represents a public, read-only share link for a file.

| Field        | Type          | Notes                                             |
|--------------|---------------|---------------------------------------------------|
| id           | UUID / BIGINT | Primary key                                       |
| file_id      | FK(File)      | The shared file                                   |
| user_id      | FK(User)      | Owner who created the share link                  |
| token        | STRING        | Random, unguessable token used in the URL        |
| expires_at   | TIMESTAMP     | Nullable; if set and in the past, link is invalid |
| is_disabled  | BOOLEAN       | If true, link is invalid                          |
| created_at   | TIMESTAMP     |                                                   |
| updated_at   | TIMESTAMP     |                                                   |

---

### 2.5 ChangeLog (for Sync / Delta)

Represents a change event for a user's folders/files. Used only by the delta mechanism.

| Field       | Type          | Notes                                                    |
|-------------|---------------|----------------------------------------------------------|
| id          | BIGSERIAL     | Primary key; also the cursor for the delta mechanism    |
| user_id     | FK(User)      | The user this change belongs to                         |
| entity_type | STRING        | `FILE` or `FOLDER`                                      |
| entity_id   | UUID / BIGINT | ID of the file/folder                                   |
| op          | STRING        | `CREATE`, `UPDATE`, or `DELETE`                         |
| snapshot    | JSON / JSONB  | Minimal representation of the current state (optional)  |
| created_at  | TIMESTAMP     |                                                          |
