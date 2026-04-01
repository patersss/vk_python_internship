from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.user_model import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_user(self, user: User) -> User:
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def get_all_users(self) -> list[User]:
        result = await self._session.execute(select(User))
        return list(result.scalars().all())

    async def get_first_available_user(self, current_time: datetime) -> User:
        query = (select(User)
                 .where((User.locktime.is_(None)) | (User.locktime <= current_time))
                 .order_by(User.created_at)
                 .limit(1)
                 .with_for_update(skip_locked=True))
        result = await self._session.execute(query)
        return result.scalars().first()

    async def lock_user(self, user_id: UUID, lock_until: datetime) -> type[User] | None:
        user = await self._session.get(User, user_id)
        if user is None:
            return None
        user.locktime = lock_until
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def free_all_users(self) -> int:
        result = await self._session.execute(
            update(User)
            .where(User.locktime.is_not(None))
            .values(locktime=None))
        return result.rowcount
