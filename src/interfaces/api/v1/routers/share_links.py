from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

from src.application.files.use_cases import (
    CreateShareLinkUseCase,
    DisableShareLinkUseCase,
    AccessShareLinkUseCase,
)
from src.application.files.dto import CreateShareLinkInputDTO, AccessShareLinkInputDTO
from src.domain.files.exceptions import (
    FileNotFound,
    ShareLinkNotFound,
    ShareLinkDisabled,
    ShareLinkExpired,
)
from src.domain.user.entity import User
from src.interfaces.api.dependencies import (
    get_current_user,
    get_create_share_link_use_case,
    get_disable_share_link_use_case,
    get_access_share_link_use_case,
)
from src.interfaces.schemas.file import (
    CreateShareLinkRequest,
    ShareLinkResponse,
    AccessShareLinkResponse,
)

router = APIRouter()


@router.post("/share-links", response_model=ShareLinkResponse, status_code=status.HTTP_201_CREATED)
async def create_share_link(
    request: CreateShareLinkRequest,
    current_user: User = Depends(get_current_user),
    use_case: CreateShareLinkUseCase = Depends(get_create_share_link_use_case),
):
    try:
        dto = CreateShareLinkInputDTO(
            user_id=current_user.id,
            file_id=request.file_id,
            expires_at=request.expires_at,
        )
        result = await use_case.execute(dto)
        return ShareLinkResponse.model_validate(result)
    except FileNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/share-links/{share_link_id}/disable", status_code=status.HTTP_204_NO_CONTENT)
async def disable_share_link(
    share_link_id: UUID,
    current_user: User = Depends(get_current_user),
    use_case: DisableShareLinkUseCase = Depends(get_disable_share_link_use_case),
):
    try:
        await use_case.execute(current_user.id, share_link_id)
    except ShareLinkNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/public/share/{token}", response_model=AccessShareLinkResponse)
async def access_share_link(
    token: str,
    use_case: AccessShareLinkUseCase = Depends(get_access_share_link_use_case),
):
    try:
        url = await use_case.execute(AccessShareLinkInputDTO(token=token))
        # Prefer redirect for usability; also return in body for clients
        return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)
    except (ShareLinkNotFound, ShareLinkDisabled, ShareLinkExpired, FileNotFound) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
