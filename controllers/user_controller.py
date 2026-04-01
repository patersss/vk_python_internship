from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
from schemas.user_schemas import UserResponse, UserCreate, UserLockResponse
from services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


def _get_service(session: AsyncSession = Depends(get_session)) -> UserService:
    """Фабрика UserService для внедрения через Depends
        Return:
            UserService
    """
    return UserService(session)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
    summary="Created a new user",
    responses={
        409: {"description": "User with this login already exists"},
        422: {"description": "Validation error"},
    })
async def create_user(user_data: UserCreate, service: UserService = Depends(_get_service)) -> UserResponse:
    """Создать нового пользователя ботофермы.Пароль сохраняется в зашифрованном виде
        Raises:
            HTTPException 409: если пользователь с таким login уже существует.
            HTTPException 422: если данные не прошли валидацию.
        Return:
            UserResponse
    """
    user = await service.create_user(user_data)
    return UserResponse.model_validate(user, from_attributes=True)


@router.get(
    "",
    response_model=list[UserResponse],
    summary="List all bot users"
)
async def get_users(service: UserService = Depends(_get_service)) -> list[UserResponse]:
    """Получить список всех ботов
        Returns:
            list[UserResponse]
    """
    list_of_users = await service.get_users()
    return [UserResponse.model_validate(u, from_attributes=True) for u in list_of_users]



@router.post(
    "/lock",
    response_model=UserLockResponse,
    summary="Lock a user for E2E test",
    responses={
        404: {"description": "No available users to lock"},
    }
)
async def lock_user(service: UserService = Depends(_get_service)) -> UserLockResponse:
    """Заблокировать первого доступного пользователя для теста. Возвращает данные пользователя с расшифрованным пароле
        Raises:
            HTTPException 404: если свободных пользователей нет.
        Returns:
            UserLockResponse
    """
    return await service.lock_user()


@router.post(
    "/free",
    summary="Unlock all users")
async def free_users(service: UserService = Depends(_get_service)) -> dict:
    """Снять блокировку со всех пользователей ботофермы
        Returns:
            dict
    """
    count = await service.free_users()
    return {"detail": f"Unlocked {count} users"}
