from src.core.exceptions import ConflictError, UnauthorizedError


class EmailExistsError(ConflictError):
    code = "EMAIL_EXISTS"
    message = "Email already registered"


class InvalidCredentialsError(UnauthorizedError):
    code = "INVALID_CREDENTIALS"
    message = "Invalid credentials"


class TokenExpiredError(UnauthorizedError):
    code = "TOKEN_EXPIRED"
    message = "Token expired"


class InvalidTokenError(UnauthorizedError):
    code = "INVALID_TOKEN"
    message = "Invalid token"


class NotAuthenticatedError(UnauthorizedError):
    code = "NOT_AUTHENTICATED"
    message = "Not authenticated"
