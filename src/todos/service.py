from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.categories.exceptions import CategoryNotFoundError
from src.categories.service import CategoryService
from src.todos.exceptions import TodoNotFoundError
from src.todos.models import Todo, TodoStatus
from src.todos.schemas import TodoCreate, TodoFilters, TodoUpdate


class TodoService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, todo_id: int, user_id: int) -> Todo | None:
        result = await self.db.execute(
            select(Todo).where(
                Todo.id == todo_id,
                Todo.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_or_404(self, todo_id: int, user_id: int) -> Todo:
        todo = await self.get_by_id(todo_id, user_id)
        if todo is None:
            raise TodoNotFoundError()
        return todo

    async def list_by_user(
        self, user_id: int, filters: TodoFilters | None = None
    ) -> list[Todo]:
        query = select(Todo).where(Todo.user_id == user_id)

        if filters:
            if filters.status is not None:
                query = query.where(Todo.status == filters.status.value)
            if filters.priority is not None:
                query = query.where(Todo.priority == filters.priority)
            if filters.category_id is not None:
                query = query.where(Todo.category_id == filters.category_id)
            if filters.due_before is not None:
                query = query.where(Todo.due_date <= filters.due_before)
            if filters.due_after is not None:
                query = query.where(Todo.due_date >= filters.due_after)

        query = query.order_by(Todo.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def _validate_category(
        self, category_id: int | None, user_id: int
    ) -> None:
        if category_id is not None:
            category = await CategoryService(self.db).get_by_id(category_id, user_id)
            if category is None:
                raise CategoryNotFoundError()

    async def create(self, data: TodoCreate, user_id: int) -> Todo:
        await self._validate_category(data.category_id, user_id)

        todo = Todo(
            user_id=user_id,
            title=data.title,
            description=data.description,
            priority=data.priority,
            due_date=data.due_date,
            category_id=data.category_id,
        )
        self.db.add(todo)
        await self.db.flush()
        await self.db.refresh(todo)
        return todo

    async def update(self, todo_id: int, data: TodoUpdate, user_id: int) -> Todo:
        todo = await self.get_by_id_or_404(todo_id, user_id)

        # Validate category if being updated
        if data.category_id is not None:
            await self._validate_category(data.category_id, user_id)

        update_data = data.model_dump(exclude_unset=True)

        # Handle status changes for completed_at
        if "status" in update_data:
            new_status = update_data["status"]
            if isinstance(new_status, TodoStatus):
                update_data["status"] = new_status.value

            if new_status == TodoStatus.COMPLETED and todo.status != TodoStatus.COMPLETED.value:
                update_data["completed_at"] = datetime.now(UTC)
            elif new_status != TodoStatus.COMPLETED and todo.status == TodoStatus.COMPLETED.value:
                update_data["completed_at"] = None

        for key, value in update_data.items():
            setattr(todo, key, value)

        await self.db.flush()
        await self.db.refresh(todo)
        return todo

    async def delete(self, todo_id: int, user_id: int) -> None:
        todo = await self.get_by_id_or_404(todo_id, user_id)
        await self.db.delete(todo)
        await self.db.flush()
