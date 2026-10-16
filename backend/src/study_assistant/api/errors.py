from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from study_assistant.domain.errors import Conflict, InvalidRequest, NotAllowed, NotFound, StudyAssistantError

STATUS = {InvalidRequest: 422, NotAllowed: 403, NotFound: 404, Conflict: 409}


def add_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(StudyAssistantError)
    async def handle(_: Request, error: StudyAssistantError) -> JSONResponse:
        return JSONResponse(status_code=STATUS.get(type(error), 400), content={"detail": str(error)})
