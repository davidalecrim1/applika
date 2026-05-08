from typing import List

from fastapi import APIRouter, Response

from app.application.dto.api_key import ApiKeyCreateDTO, ApiKeyRenameDTO
from app.application.use_cases.api_keys.create_api_key import (
    CreateApiKeyUseCase,
)
from app.application.use_cases.api_keys.delete_api_key import (
    DeleteApiKeyUseCase,
)
from app.application.use_cases.api_keys.list_api_keys import (
    ListApiKeysUseCase,
)
from app.application.use_cases.api_keys.rename_api_key import (
    RenameApiKeyUseCase,
)
from app.lib.types import SnowflakeID
from app.presentation.dependencies import ApiKeyRepositoryDp, CurrentUserDp
from app.presentation.schemas import DetailSchema
from app.presentation.schemas.api_key import (
    ApiKeyItemSchema,
    CreateApiKeyRequest,
    CreatedApiKeySchema,
    RenameApiKeyRequest,
)

router = APIRouter(
    tags=['API Keys'],
    responses={'403': {'model': DetailSchema}},
)


@router.get('/users/me/api-keys', response_model=List[ApiKeyItemSchema])
async def list_api_keys(
    c_user: CurrentUserDp,
    api_key_repo: ApiKeyRepositoryDp,
):
    """List the signed-in user's API keys without exposing raw secrets."""
    use_case = ListApiKeysUseCase(api_key_repo)
    items = await use_case.execute(c_user.id)
    return [ApiKeyItemSchema.model_validate(item) for item in items]


@router.post(
    '/users/me/api-keys',
    response_model=CreatedApiKeySchema,
    status_code=201,
)
async def create_api_key(
    payload: CreateApiKeyRequest,
    c_user: CurrentUserDp,
    api_key_repo: ApiKeyRepositoryDp,
):
    """Generate a new API key and reveal the raw key only once."""
    use_case = CreateApiKeyUseCase(api_key_repo)
    item = await use_case.execute(
        c_user.id,
        ApiKeyCreateDTO(name=payload.name),
    )
    return CreatedApiKeySchema.model_validate(item)


@router.patch(
    '/users/me/api-keys/{api_key_id}',
    response_model=ApiKeyItemSchema,
    responses={'404': {'model': DetailSchema}},
)
async def rename_api_key(
    api_key_id: SnowflakeID,
    payload: RenameApiKeyRequest,
    c_user: CurrentUserDp,
    api_key_repo: ApiKeyRepositoryDp,
):
    """Rename an API key alias without changing the key itself."""
    use_case = RenameApiKeyUseCase(api_key_repo)
    item = await use_case.execute(
        int(api_key_id),
        c_user.id,
        ApiKeyRenameDTO(name=payload.name),
    )
    return ApiKeyItemSchema.model_validate(item)


@router.delete(
    '/users/me/api-keys/{api_key_id}',
    status_code=204,
    responses={'404': {'model': DetailSchema}},
)
async def delete_api_key(
    api_key_id: SnowflakeID,
    c_user: CurrentUserDp,
    api_key_repo: ApiKeyRepositoryDp,
    response: Response,
):
    """Delete an API key so it can no longer authenticate MCP requests."""
    use_case = DeleteApiKeyUseCase(api_key_repo)
    await use_case.execute(int(api_key_id), c_user.id)
    response.status_code = 204
