from app.application.dto.api_key import ApiKeyListItemDTO
from app.core.api_keys import mask_api_key
from app.domain.repositories.api_key_repository import ApiKeyRepository


class ListApiKeysUseCase:
    def __init__(self, api_key_repo: ApiKeyRepository):
        self.api_key_repo = api_key_repo

    async def execute(self, user_id: int) -> list[ApiKeyListItemDTO]:
        api_keys = await self.api_key_repo.list_by_user_id(user_id)
        return [
            ApiKeyListItemDTO(
                id=api_key.id,
                name=api_key.name,
                masked_key=mask_api_key(api_key.last4),
                last4=api_key.last4,
                created_at=api_key.created_at,
                updated_at=api_key.updated_at,
                last_used_at=api_key.last_used_at,
            )
            for api_key in api_keys
        ]
