import hmac

from fastapi import HTTPException, status

from app.application.dto.user import UserDTO
from app.core.api_keys import parse_api_key, verify_api_key
from app.domain.repositories.api_key_repository import ApiKeyRepository
from app.domain.repositories.user_repository import UserRepository


class AuthenticateApiKeyUseCase:
    def __init__(
        self,
        api_key_repo: ApiKeyRepository,
        user_repo: UserRepository,
    ):
        self.api_key_repo = api_key_repo
        self.user_repo = user_repo

    async def execute(self, api_key: str | None) -> UserDTO:
        if not api_key:
            raise self._unauthorized('Not authenticated')

        try:
            key_id, secret = parse_api_key(api_key)
        except ValueError:
            raise self._unauthorized('Invalid API key')

        stored_key = await self.api_key_repo.get_by_key_id(key_id)
        if not stored_key:
            raise self._unauthorized('Invalid API key')

        if not verify_api_key(secret, stored_key.key_hash):
            raise self._unauthorized('Invalid API key')

        user = await self.user_repo.get_by_id(stored_key.user_id)
        if not user:
            raise self._unauthorized('User not found')

        await self.api_key_repo.touch_last_used(stored_key)
        return UserDTO.model_validate(user)

    def _unauthorized(self, detail: str) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )
