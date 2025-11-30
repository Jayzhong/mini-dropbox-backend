from fastapi import FastAPI
from src.interfaces.api.v1.routers import system, auth

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

@app.get("/")
async def root():
    return {"message": "Mini Dropbox API is running"}
