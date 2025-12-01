from datetime import datetime, timedelta, timezone
from typing import Dict, Any
import jwt
from src.application.common.interfaces import TokenService
from src.infrastructure.config.settings import settings

class JwtTokenService(TokenService):
    """
    Implementation of TokenService using PyJWT.
    """
    def create_access_token(self, data: Dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def decode_access_token(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except jwt.PyJWTError as e:
            raise ValueError("Could not validate credentials") from e
