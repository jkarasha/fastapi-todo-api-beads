from src.core.exceptions import NotFoundError


class TodoNotFoundError(NotFoundError):
    code = "TODO_NOT_FOUND"
    message = "Todo not found"
