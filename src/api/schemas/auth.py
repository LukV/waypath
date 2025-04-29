from pydantic import BaseModel


class TokenPair(BaseModel):  # noqa: D101
    access_token: str
    refresh_token: str
    token_type: str


class LoginRequest(BaseModel):  # noqa: D101
    username: str
    password: str
