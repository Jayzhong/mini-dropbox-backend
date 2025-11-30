from fastapi import APIRouter, Depends
from src.application.system.use_cases import GetSystemHealthUseCase
from src.interfaces.api.dependencies import get_health_use_case
from src.interfaces.schemas.system import SystemHealthResponse

router = APIRouter()

@router.get("/health", response_model=SystemHealthResponse)
async def check_health(
    use_case: GetSystemHealthUseCase = Depends(get_health_use_case)
):
    """
    Deep Health Check Endpoint.
    Traverses: API -> UseCase -> Repo -> DB -> Repo -> UseCase -> API
    """
    health_entity = await use_case.execute()
    
    # Convert Domain Entity -> Pydantic Response
    return SystemHealthResponse(
        database_time=health_entity.database_time,
        status=health_entity.status
    )
