class AppException(Exception):
    code: str = "APP_ERROR"
    message: str = "An application error occurred"
    status_code: int = 400

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.__class__.message
        super().__init__(self.message)


class NotFoundError(AppException):
    code = "NOT_FOUND"
    message = "Resource not found"
    status_code = 404


class ConflictError(AppException):
    code = "CONFLICT"
    message = "Resource already exists"
    status_code = 409


class UnauthorizedError(AppException):
    code = "UNAUTHORIZED"
    message = "Not authenticated"
    status_code = 401


class ForbiddenError(AppException):
    code = "FORBIDDEN"
    message = "Access denied"
    status_code = 403


class ValidationError(AppException):
    code = "VALIDATION_ERROR"
    message = "Validation failed"
    status_code = 422
