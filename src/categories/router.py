from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.categories.dependencies import get_category_or_404
from src.categories.models import Category
from src.categories.schemas import CategoryCreate, CategoryResponse, CategoryUpdate
from src.categories.service import CategoryService
from src.core.database import get_db

router = APIRouter()


@router.get(
    "",
    response_model=list[CategoryResponse],
)
async def list_categories(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[Category]:
    """List all categories for the current user."""
    return await CategoryService(db).list_by_user(current_user.id)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "Category already exists"}},
)
async def create_category(
    data: CategoryCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Category:
    """Create a new category."""
    return await CategoryService(db).create(data, current_user.id)


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    responses={404: {"description": "Category not found"}},
)
async def get_category(
    category: Annotated[Category, Depends(get_category_or_404)],
) -> Category:
    """Get a category by ID."""
    return category


@router.patch(
    "/{category_id}",
    response_model=CategoryResponse,
    responses={
        404: {"description": "Category not found"},
        409: {"description": "Category already exists"},
    },
)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Category:
    """Update a category."""
    return await CategoryService(db).update(category_id, data, current_user.id)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Category not found"}},
)
async def delete_category(
    category_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete a category."""
    await CategoryService(db).delete(category_id, current_user.id)
