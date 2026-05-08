from app.core.exceptions import ResourceNotFound
from app.domain.repositories.api_key_repository import ApiKeyRepository


class DeleteApiKeyUseCase:
    def __init__(self, api_key_repo: ApiKeyRepository):
        self.api_key_repo = api_key_repo

    async def execute(self, api_key_id: int, user_id: int) -> None:
        deleted = await self.api_key_repo.delete(api_key_id, user_id)
        if not deleted:
            raise ResourceNotFound('API key not found')
