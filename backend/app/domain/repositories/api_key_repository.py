from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import ApiKeyModel


class ApiKeyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, api_key: ApiKeyModel) -> ApiKeyModel:
        try:
            self.session.add(api_key)
            await self.session.commit()
            await self.session.refresh(api_key)
            return api_key
        except Exception as e:
            await self.session.rollback()
            raise e

    async def list_by_user_id(self, user_id: int) -> list[ApiKeyModel]:
        result = await self.session.scalars(
            select(ApiKeyModel)
            .where(ApiKeyModel.user_id == user_id)
            .order_by(ApiKeyModel.created_at.desc())
        )
        return list(result)

    async def get_by_id_and_user_id(
        self,
        api_key_id: int,
        user_id: int,
    ) -> ApiKeyModel | None:
        return await self.session.scalar(
            select(ApiKeyModel).where(
                ApiKeyModel.id == api_key_id,
                ApiKeyModel.user_id == user_id,
            )
        )

    async def get_by_key_id(self, key_id: str) -> ApiKeyModel | None:
        return await self.session.scalar(
            select(ApiKeyModel).where(ApiKeyModel.key_id == key_id)
        )

    async def update(self, api_key: ApiKeyModel) -> ApiKeyModel:
        try:
            api_key.updated_at = datetime.now(timezone.utc)
            self.session.add(api_key)
            await self.session.commit()
            await self.session.refresh(api_key)
            return api_key
        except Exception as e:
            await self.session.rollback()
            raise e

    async def delete(self, api_key_id: int, user_id: int) -> int:
        try:
            result = await self.session.execute(
                delete(ApiKeyModel).where(
                    ApiKeyModel.id == api_key_id,
                    ApiKeyModel.user_id == user_id,
                )
            )
            await self.session.commit()
            return result.rowcount
        except Exception as e:
            await self.session.rollback()
            raise e

    async def touch_last_used(self, api_key: ApiKeyModel) -> ApiKeyModel:
        try:
            api_key.last_used_at = datetime.now(timezone.utc)
            self.session.add(api_key)
            await self.session.commit()
            await self.session.refresh(api_key)
            return api_key
        except Exception as e:
            await self.session.rollback()
            raise e
