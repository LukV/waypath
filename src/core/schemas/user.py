from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class PasswordValidationMixin:
    """Mixin to add password validation logic."""

    @staticmethod
    def validate_password(password: str) -> str:
        """Validate that a password meets the required constraints."""
        if len(password) < 8 or len(password) > 128:  # noqa: PLR2004
            raise ValueError("Password must be between 8 and 128 characters long.")  # noqa: TRY003
        if not any(c.isalpha() for c in password):
            raise ValueError("Password must include at least one letter.")  # noqa: TRY003
        if not any(c.isdigit() for c in password):
            raise ValueError("Password must include at least one number.")  # noqa: TRY003
        return password


class UserCreate(BaseModel, PasswordValidationMixin):  # noqa: D101
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="The username for the new user. Must be unique.",
    )
    email: EmailStr = Field(
        ..., description="The email address for the new user. Must be unique."
    )
    password: str | None = Field(
        None,
        description=(
            "The password for the new user. Must be 8-128 characters long and include "
            "at least one letter and one number. Required unless using external "
            "authentication."
        ),
    )

    @model_validator(mode="before")
    def validate_fields(cls, data: dict[str, Any]) -> dict[str, Any]:  # noqa: D102, N805
        password = data.get("password")
        if password:
            data["password"] = cls.validate_password(password)
        return data


class UserResponse(BaseModel):  # noqa: D101
    id: str = Field(..., description="A unique public identifier for the user.")
    username: str = Field(..., description="The username of the user.")
    email: EmailStr = Field(..., description="The email address of the user.")
    date_created: datetime = Field(
        ..., description="The timestamp when the user was created."
    )

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):  # noqa: D101
    username: str | None = Field(
        None,
        min_length=3,
        max_length=50,
        description="The updated username. Must be unique.",
    )
    email: EmailStr | None = Field(
        None, description="The updated email address. Must be unique."
    )

    model_config = ConfigDict(from_attributes=True)


class AdminUserUpdate(UserUpdate):  # noqa: D101
    role: str | None = Field(
        None, description="The role of the user. Only settable by admins."
    )


class AdminUserResponse(UserResponse):  # noqa: D101
    role: str  # Include 'role' only for admin responses


class PasswordChange(BaseModel, PasswordValidationMixin):  # noqa: D101
    new_password: str = Field(
        ...,
        description=(
            "The new password for the user. Must be 8-128 characters long and include "
            "at least one letter and one number."
        ),
    )

    @model_validator(mode="before")
    def validate_fields(cls, values: dict[str, Any]) -> dict[str, Any]:  # noqa: D102, N805
        values["new_password"] = cls.validate_password(values["new_password"])
        return values


class PasswordResetRequest(BaseModel):  # noqa: D101
    email: EmailStr = Field(
        ..., description="The email address associated with the user account."
    )


class PasswordReset(BaseModel, PasswordValidationMixin):  # noqa: D101
    email: EmailStr = Field(
        ..., description="The email address associated with the user account."
    )
    new_password: str = Field(
        ...,
        description=(
            "The new password for the user. Must be 8-128 characters long and include "
            "at least one letter and one number."
        ),
    )
    token: str = Field(
        ...,
        description="The token sent to the user for verifying the  reset request.",
    )

    @model_validator(mode="before")
    def validate_fields(cls, values: dict[str, Any]) -> dict[str, Any]:  # noqa: D102, N805
        values["new_password"] = cls.validate_password(values["new_password"])
        return values
