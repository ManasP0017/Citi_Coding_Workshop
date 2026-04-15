"""Global exception handlers — consistent JSON error envelope."""

import logging

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.warning("HTTP %d – %s %s – %s", exc.status_code, request.method, request.url, exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail, "code": exc.status_code},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = [
            {"field": " → ".join(str(l) for l in e["loc"][1:]), "msg": e["msg"]}
            for e in exc.errors()
        ]
        logger.warning("Validation error on %s %s: %s", request.method, request.url, errors)
        return JSONResponse(
            status_code=422,
            content={"error": "Validation failed", "code": 422, "details": errors},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception on %s %s", request.method, request.url)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "code": 500},
        )
