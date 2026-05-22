from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class UserRegisterRequest(BaseModel):
    """Corpo de `POST /auth/register`."""

    username: str = Field(
        min_length=3,
        max_length=50,
        description="Nome de usuário único (3–50 caracteres).",
        examples=["alice"],
    )
    password: str = Field(
        min_length=6,
        max_length=128,
        description="Senha em texto plano (mínimo 6 caracteres; armazenada com hash).",
        json_schema_extra={"format": "password"},
    )


class LoginRequest(BaseModel):
    """Corpo de `POST /auth/login`."""

    username: str = Field(
        min_length=3,
        max_length=50,
        description="Nome de usuário cadastrado.",
        examples=["alice"],
    )
    password: str = Field(
        min_length=6,
        max_length=128,
        description="Senha do usuário.",
        json_schema_extra={"format": "password"},
    )


class TokenResponse(BaseModel):
    """Token JWT retornado após login bem-sucedido."""

    access_token: str = Field(
        description="JWT para enviar no header `Authorization: Bearer <token>`.",
    )
    token_type: Literal["bearer"] = Field(
        default="bearer",
        description="Esquema de autenticação (sempre `bearer`).",
    )


class UserRead(BaseModel):
    """Representação pública do usuário (sem senha)."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Identificador interno do usuário.")
    username: str = Field(description="Nome de usuário.")
