from fastapi import APIRouter, Depends, HTTPException, status
from src.application.user.use_cases import RegisterUserUseCase
from src.application.user.dto import UserOutputDTO
from src.domain.user.exceptions import UserAlreadyExistsError
from src.interfaces.api.dependencies import get_register_user_use_case
from src.interfaces.schemas.user import RegisterUserRequest, UserResponse

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    request: RegisterUserRequest,
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case)
):
    """
    Registers a new user in the system.
    """
    try:
        user_output_dto: UserOutputDTO = await use_case.execute(request)
        return UserResponse(
            id=user_output_dto.id,
            email=user_output_dto.email,
            created_at=user_output_dto.created_at,
            updated_at=user_output_dto.updated_at
        )
    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists."
        )
    except Exception as e:
        # Generic error handler, specific domain errors should be caught above
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}"
        )
