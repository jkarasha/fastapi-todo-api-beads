from datetime import datetime

from pydantic import Field

from src.core.schemas import BaseSchema


class CategoryCreate(BaseSchema):
    name: str = Field(min_length=1, max_length=100)


class CategoryUpdate(BaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=100)


class CategoryResponse(BaseSchema):
    id: int
    name: str
    created_at: datetime
