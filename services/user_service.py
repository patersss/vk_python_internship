from datetime import timezone, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from models.user_model import User
from repositories.user_repository import UserRepository
from schemas.user_schemas import UserCreate, UserLockResponse
from security.security import encrypt, decrypt


class UserService:
    """Сервис для управления пользователями ботофермы"""
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._user_repository = UserRepository(session)

    async def create_user(self, user_data: UserCreate) -> User:
        """Создать нового пользователя с зашифрованным паролем
            Raises:
                HTTPException: если пользователь с таким login уже существует
            Returns:
                User
        """
        user = User(
            login=user_data.login,
            password=encrypt(user_data.password),
            project_id=user_data.project_id,
            env=user_data.env,
            domain=user_data.domain
        )
        try:
            await self._user_repository.create_user(user)
            await self._session.commit()
        except IntegrityError:
            await self._session.rollback()
            raise HTTPException(status_code=409, detail=f"User with login {user_data.login} already exists")
        return user

    async def get_users(self) -> list[User]:
        """Получить список всех зарегистрированных пользователей
            Returns:
                list[User]
        """
        return await self._user_repository.get_all_users()

    async def lock_user(self) -> UserLockResponse | None:
        """Найти и заблокировать первого доступного пользователя. Устанавливает locktime на
         текущее время + lock_timeout_seconds(по дефолту = 300 секунд)
            Raises:
                 HTTPException: если нет ни одного доступного для блокировки пользователя
            Returns:
                Данные пользователя с расшифрованным паролем
                или None, если свободных пользователей нет.
        """
        now = datetime.now(timezone.utc)
        user = await self._user_repository.get_first_available_user(now)
        if user is None:
            raise HTTPException(status_code=404, detail="No available users to lock")

        lock_until = now + timedelta(seconds=settings.lock_timeout_seconds)
        await self._user_repository.lock_user(user.id, lock_until)
        await self._session.commit()

        return UserLockResponse(
            login=user.login,
            password=decrypt(user.password),
            created_at=user.created_at,
            project_id=user.project_id,
            env=user.env,
            domain=user.domain,
            locktime=user.locktime
        )

    async def free_users(self) -> int:
        """Снять блокировку со всех пользователей
            Returns:
                Количество разблокированных пользователей.
        """
        count = await self._user_repository.free_all_users()
        await self._session.commit()
        return count