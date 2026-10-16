from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger

from study_assistant.domain.errors import (
    Conflict,
    InvalidRequest,
    NotAllowed,
    NotFound,
    StudyAssistantError,
    TooLarge,
)
from study_assistant.platform.port import PlatformError

STATUS = {InvalidRequest: 422, NotAllowed: 403, NotFound: 404, Conflict: 409, TooLarge: 413}


def add_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(StudyAssistantError)
    async def handle(_: Request, error: StudyAssistantError) -> JSONResponse:
        return JSONResponse(status_code=STATUS.get(type(error), 400), content={"detail": str(error)})

    @app.exception_handler(PlatformError)
    async def handle_platform(_: Request, error: PlatformError) -> JSONResponse:
        logger.error(f"the platform failed: {error}")
        return JSONResponse(status_code=502, content={"detail": f"The gogi platform failed: {error}"})
