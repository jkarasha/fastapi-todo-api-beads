from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.categories.models import Category
from src.categories.service import CategoryService
from src.core.database import get_db


async def get_category_or_404(
    category_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Category:
    return await CategoryService(db).get_by_id_or_404(category_id, current_user.id)
