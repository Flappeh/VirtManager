import uuid

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    is_active: bool = True
    is_superuser: bool = False

class UserEmail(SQLModel):
    email: EmailStr = Field(max_length=255)

class UserName(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)

class UserFlags(SQLModel):
    is_active: bool = True
    is_superuser: bool = False

# Properties to receive via API on creation
class UserCreate(SQLModel):
    email: EmailStr = Field(max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

# Properties to return via API, id is always required
class UserPublic(SQLModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str | None
    is_active: bool
    is_superuser: bool

class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int

class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)