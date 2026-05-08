from app.application.dto.api_key import (
    ApiKeyCreateDTO,
    ApiKeyCreateResultDTO,
)
from app.core.api_keys import derive_api_key_hash, generate_api_key, mask_api_key
from app.domain.models import ApiKeyModel
from app.domain.repositories.api_key_repository import ApiKeyRepository


class CreateApiKeyUseCase:
    def __init__(self, api_key_repo: ApiKeyRepository):
        self.api_key_repo = api_key_repo

    async def execute(
        self,
        user_id: int,
        data: ApiKeyCreateDTO,
    ) -> ApiKeyCreateResultDTO:
        generated = generate_api_key()
        api_key = await self.api_key_repo.create(
            ApiKeyModel(
                user_id=user_id,
                name=data.name,
                key_id=generated.key_id,
                key_hash=derive_api_key_hash(generated.secret),
                last4=generated.last4,
            )
        )
        return ApiKeyCreateResultDTO(
            id=api_key.id,
            name=api_key.name,
            masked_key=mask_api_key(api_key.last4),
            last4=api_key.last4,
            created_at=api_key.created_at,
            updated_at=api_key.updated_at,
            last_used_at=api_key.last_used_at,
            key=generated.full_key,
        )
