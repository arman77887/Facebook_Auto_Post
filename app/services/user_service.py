from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.all_models import User
from app.config import settings


class UserService:
    @staticmethod
    async def get_or_create_user(
        db: AsyncSession,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        result = await db.execute(select(User).filter(User.telegram_id == telegram_id))
        user = result.scalars().first()
        if not user:
            is_admin = (telegram_id == settings.ADMIN_TELEGRAM_ID)
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                is_admin=is_admin,
                timezone="UTC"
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        return user

    @staticmethod
    async def update_timezone(db: AsyncSession, user_id: int, timezone_str: str) -> bool:
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        if user:
            user.timezone = timezone_str
            await db.commit()
            return True
        return False
