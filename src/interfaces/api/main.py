from fastapi import FastAPI
from src.interfaces.api.v1.routers import system, auth, folders, files, share_links

app = FastAPI(
    title="Mini Dropbox Backend",
    description="A personal file storage MVP using DDD & Clean Architecture",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Include Routers
app.include_router(system.router, prefix="/api/v1/system", tags=["System"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(folders.router, prefix="/api/v1", tags=["Folders"]) # Prefix /api/v1 for folders
app.include_router(files.router, prefix="/api/v1", tags=["Files"]) # Prefix /api/v1 for files
app.include_router(share_links.router, prefix="/api/v1", tags=["Share Links"])

@app.get("/")
async def root():
    return {"message": "Mini Dropbox API is running"}
