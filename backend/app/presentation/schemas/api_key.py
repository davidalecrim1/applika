from datetime import datetime

from pydantic import BaseModel, Field

from app.lib.types import SnowflakeID
from app.presentation.schemas import BaseSchema, TimeSchema


class CreateApiKeyRequest(BaseSchema):
    name: str = Field(min_length=1, max_length=200)


class RenameApiKeyRequest(BaseSchema):
    name: str = Field(min_length=1, max_length=200)


class ApiKeyItemSchema(BaseModel):
    id: SnowflakeID
    name: str
    masked_key: str
    last4: str
    created_at: datetime
    updated_at: datetime | None = None
    last_used_at: datetime | None = None


class CreatedApiKeySchema(ApiKeyItemSchema):
    key: str
