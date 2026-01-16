from datetime import date, datetime

from pydantic import Field

from src.core.schemas import BaseSchema
from src.todos.models import TodoStatus


class TodoCreate(BaseSchema):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    priority: int | None = Field(default=None, ge=0, le=4)
    due_date: date | None = None
    category_id: int | None = None


class TodoUpdate(BaseSchema):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: TodoStatus | None = None
    priority: int | None = Field(default=None, ge=0, le=4)
    due_date: date | None = None
    category_id: int | None = None


class TodoResponse(BaseSchema):
    id: int
    title: str
    description: str | None
    status: str
    priority: int | None
    due_date: date | None
    category_id: int | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None


class TodoFilters(BaseSchema):
    status: TodoStatus | None = None
    priority: int | None = Field(default=None, ge=0, le=4)
    category_id: int | None = None
    due_before: date | None = None
    due_after: date | None = None
