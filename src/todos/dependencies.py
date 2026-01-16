from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.core.database import get_db
from src.todos.models import Todo
from src.todos.service import TodoService


async def get_todo_or_404(
    todo_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Todo:
    return await TodoService(db).get_by_id_or_404(todo_id, current_user.id)
