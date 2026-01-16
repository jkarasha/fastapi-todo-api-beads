from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.categories.exceptions import CategoryExistsError, CategoryNotFoundError
from src.categories.models import Category
from src.categories.schemas import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, category_id: int, user_id: int) -> Category | None:
        result = await self.db.execute(
            select(Category).where(
                Category.id == category_id,
                Category.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_or_404(self, category_id: int, user_id: int) -> Category:
        category = await self.get_by_id(category_id, user_id)
        if category is None:
            raise CategoryNotFoundError()
        return category

    async def list_by_user(self, user_id: int) -> list[Category]:
        result = await self.db.execute(
            select(Category)
            .where(Category.user_id == user_id)
            .order_by(Category.name)
        )
        return list(result.scalars().all())

    async def create(self, data: CategoryCreate, user_id: int) -> Category:
        category = Category(
            name=data.name,
            user_id=user_id,
        )
        self.db.add(category)
        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise CategoryExistsError() from None
        await self.db.refresh(category)
        return category

    async def update(
        self, category_id: int, data: CategoryUpdate, user_id: int
    ) -> Category:
        category = await self.get_by_id_or_404(category_id, user_id)

        if data.name is not None:
            category.name = data.name

        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise CategoryExistsError() from None
        await self.db.refresh(category)
        return category

    async def delete(self, category_id: int, user_id: int) -> None:
        category = await self.get_by_id_or_404(category_id, user_id)
        await self.db.delete(category)
        await self.db.flush()
