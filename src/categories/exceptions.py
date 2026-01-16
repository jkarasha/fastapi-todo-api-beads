from src.core.exceptions import ConflictError, NotFoundError


class CategoryNotFoundError(NotFoundError):
    code = "CATEGORY_NOT_FOUND"
    message = "Category not found"


class CategoryExistsError(ConflictError):
    code = "CATEGORY_EXISTS"
    message = "Category already exists"
