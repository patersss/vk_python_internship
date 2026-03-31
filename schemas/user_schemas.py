import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreate(BaseModel):
    login: EmailStr
    password: str = Field(..., min_length=8, max_length=64)
    project_id: uuid.UUID
    env: Environment
    domain: Domain


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    login: EmailStr
    created_at: datetime
    project_id: uuid.UUID
    env: Environment
    domain: Domain
    locktime: datetime | None


class UserLockResponse(BaseModel):
    login: EmailStr
    password: str
    created_at: datetime
    project_id: uuid.UUID
    env: Environment
    domain: Domain
    locktime: datetime | None