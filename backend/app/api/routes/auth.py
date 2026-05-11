from fastapi import APIRouter, HTTPException, status

from app.api.deps import UserServiceDep
from app.core.exceptions import UsernameAlreadyExistsError
from app.core.security import create_access_token
from app.schemas.auth import LoginRequest, TokenResponse, UserRead, UserRegisterRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegisterRequest, user_service: UserServiceDep) -> UserRead:
    try:
        return user_service.register(payload)
    except UsernameAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username já existe",
        ) from exc


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, user_service: UserServiceDep) -> TokenResponse:
    user = user_service.authenticate(payload.username, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(subject=user.username)
    return TokenResponse(access_token=token)
