from fastapi import Request, status
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base class for all domain-level errors. Carries an HTTP status code
    so a single exception handler can translate any of these consistently."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "Something went wrong."

    def __init__(self, message: str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "Resource not found."


class ForbiddenError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    default_message = "You do not have permission to do this."


class ConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT
    default_message = "This request conflicts with the current state of the resource."


class ValidationAppError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_message = "Invalid input."


class InsufficientInventoryError(ConflictError):
    default_message = "Not enough available inventory for this operation."


class InvalidStateTransitionError(ConflictError):
    default_message = "This status change is not allowed from the order's current status."


class DuplicateOperationError(ConflictError):
    default_message = "This operation has already been performed."


def register_exception_handlers(app):
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "error_type": exc.__class__.__name__},
        )
