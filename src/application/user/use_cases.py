from src.application.user.dto import RegisterUserInputDTO, UserOutputDTO, LoginUserInputDTO, TokenOutputDTO
from src.application.common.interfaces import UserRepository, PasswordHasher, UnitOfWork, TokenService
from src.domain.user.entity import User
from src.domain.user.exceptions import UserAlreadyExistsError, InvalidCredentialsError
import uuid
from datetime import datetime, timezone

class RegisterUserUseCase:
    """
    Application Service to register a new user.
    """
    def __init__(
        self, 
        user_repo: UserRepository, 
        password_hasher: PasswordHasher,
        uow: UnitOfWork
    ):
        self.user_repo = user_repo
        self.password_hasher = password_hasher
        self.uow = uow

    async def execute(self, input_dto: RegisterUserInputDTO) -> UserOutputDTO:
        existing_user = await self.user_repo.get_by_email(input_dto.email)
        if existing_user:
            raise UserAlreadyExistsError(input_dto.email)

        hashed_password = await self.password_hasher.hash(input_dto.password)

        new_user = User(
            id=uuid.uuid4(),
            email=input_dto.email,
            password_hash=hashed_password,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        saved_user = await self.user_repo.save(new_user)
        
        # Commit the transaction
        await self.uow.commit()

        return UserOutputDTO(
            id=str(saved_user.id),
            email=saved_user.email,
            created_at=saved_user.created_at,
            updated_at=saved_user.updated_at
        )

class LoginUserUseCase:
    """
    Application Service to log in an existing user.
    """
    def __init__(
        self,
        user_repo: UserRepository,
        password_hasher: PasswordHasher,
        token_service: TokenService,
        uow: UnitOfWork
    ):
        self.user_repo = user_repo
        self.password_hasher = password_hasher
        self.token_service = token_service
        self.uow = uow # UoW is here for consistency, though login is a read operation

    async def execute(self, input_dto: LoginUserInputDTO) -> TokenOutputDTO:
        user = await self.user_repo.get_by_email(input_dto.email)
        if not user:
            raise InvalidCredentialsError()

        if not await self.password_hasher.verify(input_dto.password, user.password_hash):
            raise InvalidCredentialsError()
        
        # Optionally update last_login or similar field, hence the UoW in init
        # For now, no changes to commit.

        access_token = self.token_service.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        return TokenOutputDTO(access_token=access_token)
