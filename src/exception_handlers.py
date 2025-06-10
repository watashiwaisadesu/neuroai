from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from src.core.base.exception import AppException

async def app_exception_handler(request: Request, exc: AppException):
    """
    Custom exception handler for AppException.
    Returns a JSON response with custom error message and code.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.message,
            "error_code": getattr(exc, "error_code", "unknown_error")
        }
    )

async def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom exception handler for FastAPI's RequestValidationError (422 Unprocessable Entity).
    Formats validation errors into a more readable JSON response.
    """
    errors = []
    for err in exc.errors():
        # Join location parts, excluding 'body'
        field = ".".join(str(loc) for loc in err['loc'] if loc != 'body')
        errors.append({
            "field": field,
            "error": err['msg']
        })

    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": HTTP_422_UNPROCESSABLE_ENTITY,
                "message": "Validation error",
                "details": errors
            }
        }
    )

