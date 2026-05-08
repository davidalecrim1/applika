from app.application.dto.api_key import ApiKeyListItemDTO, ApiKeyRenameDTO
from app.core.api_keys import mask_api_key
from app.core.exceptions import ResourceNotFound
from app.domain.repositories.api_key_repository import ApiKeyRepository


class RenameApiKeyUseCase:
    def __init__(self, api_key_repo: ApiKeyRepository):
        self.api_key_repo = api_key_repo

    async def execute(
        self,
        api_key_id: int,
        user_id: int,
        data: ApiKeyRenameDTO,
    ) -> ApiKeyListItemDTO:
        api_key = await self.api_key_repo.get_by_id_and_user_id(
            api_key_id,
            user_id,
        )
        if not api_key:
            raise ResourceNotFound('API key not found')
        api_key.name = data.name
        api_key = await self.api_key_repo.update(api_key)
        return ApiKeyListItemDTO(
            id=api_key.id,
            name=api_key.name,
            masked_key=mask_api_key(api_key.last4),
            last4=api_key.last4,
            created_at=api_key.created_at,
            updated_at=api_key.updated_at,
            last_used_at=api_key.last_used_at,
        )
