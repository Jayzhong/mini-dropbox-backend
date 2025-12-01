from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from src.application.files.dto import CreateFolderInputDTO
from src.application.files.use_cases import CreateFolderUseCase, ListFolderContentUseCase
from src.domain.files.exceptions import FolderNotFound, FolderAlreadyExists
from src.domain.user.entity import User
from src.interfaces.api.dependencies import get_current_user, get_create_folder_use_case, get_list_folder_content_use_case
from src.interfaces.schemas.file import (
    CreateFolderRequest,
    FolderResponse,
    ListContentResponse,
    FileResponse,
)

# Protect all folder routes; get_current_user caches on request.state
router = APIRouter(dependencies=[Depends(get_current_user)])

@router.post("/folders", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
async def create_folder(
    request: CreateFolderRequest,
    current_user: User = Depends(get_current_user),
    create_folder_use_case: CreateFolderUseCase = Depends(get_create_folder_use_case)
):
    """
    Create a new folder for the current user.
    """
    input_dto = CreateFolderInputDTO(
        user_id=current_user.id,
        name=request.name,
        parent_id=request.parent_id
    )
    try:
        folder = await create_folder_use_case.execute(input_dto)
        return FolderResponse.model_validate(folder)
    except FolderNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except FolderAlreadyExists as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        # Generic error handling for unexpected issues
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.get("/folders/{folder_id}/content", response_model=ListContentResponse)
@router.get("/folders/root/content", response_model=ListContentResponse)
async def list_folder_content(
    folder_id: Optional[UUID] = None, # Make folder_id optional, for root content
    current_user: User = Depends(get_current_user),
    list_folder_content_use_case: ListFolderContentUseCase = Depends(get_list_folder_content_use_case)
):
    """
    List folders and files within a specific folder or the root folder.
    """
    try:
        content = await list_folder_content_use_case.execute(current_user.id, folder_id)
        return ListContentResponse(
            folders=[FolderResponse.model_validate(f) for f in content.folders],
            files=[FileResponse.model_validate(f) for f in content.files]
        )
    except FolderNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")
