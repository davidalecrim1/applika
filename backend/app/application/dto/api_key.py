from datetime import datetime

from pydantic import BaseModel

from app.application.dto import BaseSchema


class ApiKeyDTO(BaseSchema):
    user_id: int
    name: str
    key_id: str
    key_hash: str
    last4: str
    last_used_at: datetime | None = None


class ApiKeyListItemDTO(BaseModel):
    id: int
    name: str
    masked_key: str
    last4: str
    created_at: datetime
    updated_at: datetime | None = None
    last_used_at: datetime | None = None


class ApiKeyCreateResultDTO(ApiKeyListItemDTO):
    key: str


class ApiKeyCreateDTO(BaseModel):
    name: str


class ApiKeyRenameDTO(BaseModel):
    name: str
