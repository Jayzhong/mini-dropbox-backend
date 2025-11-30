from fastapi import APIRouter, Depends, HTTPException, status
from src.application.user.use_cases import RegisterUserUseCase, LoginUserUseCase
from src.application.user.dto import UserOutputDTO, TokenOutputDTO
from src.domain.user.exceptions import UserAlreadyExistsError, InvalidCredentialsError
from src.interfaces.api.dependencies import get_register_user_use_case, get_login_user_use_case
from src.interfaces.schemas.user import RegisterUserRequest, UserResponse, LoginRequest, TokenResponse
import logging # Added for logging

router = APIRouter()

# Setup basic logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logger.exception("Error during user registration:") # Log the full traceback
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e.__class__.__name__} - {e}"
        )

@router.post("/login", response_model=TokenResponse)
async def login_user(
    request: LoginRequest,
    use_case: LoginUserUseCase = Depends(get_login_user_use_case)
):
    """
    Authenticates a user and returns an access token.
    """
    try:
        token_output_dto: TokenOutputDTO = await use_case.execute(request)
        return TokenResponse(
            access_token=token_output_dto.access_token,
            token_type=token_output_dto.token_type
        )
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.exception("Error during user login:") # Log the full traceback
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e.__class__.__name__} - {e}"
        )
