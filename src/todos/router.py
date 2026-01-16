from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.core.database import get_db
from src.todos.dependencies import get_todo_or_404
from src.todos.models import Todo, TodoStatus
from src.todos.schemas import TodoCreate, TodoFilters, TodoResponse, TodoUpdate
from src.todos.service import TodoService

router = APIRouter()


@router.get(
    "",
    response_model=list[TodoResponse],
)
async def list_todos(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    status: TodoStatus | None = Query(default=None),
    priority: int | None = Query(default=None, ge=0, le=4),
    category_id: int | None = Query(default=None),
    due_before: date | None = Query(default=None),
    due_after: date | None = Query(default=None),
) -> list[Todo]:
    """List all todos for the current user with optional filters."""
    filters = TodoFilters(
        status=status,
        priority=priority,
        category_id=category_id,
        due_before=due_before,
        due_after=due_after,
    )
    return await TodoService(db).list_by_user(current_user.id, filters)


@router.post(
    "",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    responses={404: {"description": "Category not found"}},
)
async def create_todo(
    data: TodoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Todo:
    """Create a new todo."""
    return await TodoService(db).create(data, current_user.id)


@router.get(
    "/{todo_id}",
    response_model=TodoResponse,
    responses={404: {"description": "Todo not found"}},
)
async def get_todo(
    todo: Annotated[Todo, Depends(get_todo_or_404)],
) -> Todo:
    """Get a todo by ID."""
    return todo


@router.patch(
    "/{todo_id}",
    response_model=TodoResponse,
    responses={404: {"description": "Todo or category not found"}},
)
async def update_todo(
    todo_id: int,
    data: TodoUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Todo:
    """Update a todo."""
    return await TodoService(db).update(todo_id, data, current_user.id)


@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Todo not found"}},
)
async def delete_todo(
    todo_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete a todo."""
    await TodoService(db).delete(todo_id, current_user.id)
