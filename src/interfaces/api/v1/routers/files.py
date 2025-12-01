from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from fastapi.responses import RedirectResponse
from src.application.files.dto import UploadFileInputDTO
from src.application.files.use_cases import UploadFileUseCase, DownloadFileUseCase
from src.domain.files.exceptions import FolderNotFound, FileNotFound
from src.domain.user.entity import User
from src.interfaces.api.dependencies import get_current_user, get_upload_file_use_case, get_download_file_use_case
from src.interfaces.schemas.file import FileResponse

# Protect all file routes; get_current_user caches on request.state
router = APIRouter(dependencies=[Depends(get_current_user)])

@router.post("/files", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    folder_id: UUID,
    file: UploadFile, # Corrected type hint
    current_user: User = Depends(get_current_user),
    upload_file_use_case: UploadFileUseCase = Depends(get_upload_file_use_case)
):
    """
    Upload a file to a specific folder for the current user.
    """
    try:
        content = await file.read() # Read the file content
        input_dto = UploadFileInputDTO(
            user_id=current_user.id,
            folder_id=folder_id,
            name=file.filename,
            size_bytes=len(content),
            mime_type=file.content_type if file.content_type else "application/octet-stream",
            content=content
        )
        uploaded_file = await upload_file_use_case.execute(input_dto)
        return FileResponse.model_validate(uploaded_file)
    except FolderNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.get("/files/{file_id}/download")
async def download_file(
    file_id: UUID,
    current_user: User = Depends(get_current_user),
    download_file_use_case: DownloadFileUseCase = Depends(get_download_file_use_case)
):
    """
    Generate a presigned URL to download a file.
    """
    try:
        presigned_url = await download_file_use_case.execute(current_user.id, file_id)
        return RedirectResponse(url=presigned_url, status_code=status.HTTP_302_FOUND)
    except FileNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")
