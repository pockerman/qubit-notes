from typing import Annotated

from fastapi import Header, Request

from study_assistant.domain.courses import Courses
from study_assistant.domain.materials import Materials
from study_assistant.domain.reading import Reading


def courses(request: Request) -> Courses:
    return request.app.state.courses


def materials(request: Request) -> Materials:
    return request.app.state.materials


def reading(request: Request) -> Reading:
    return request.app.state.reading


# the student making the request. There is no authentication yet: the client says who it is
Student = Annotated[str, Header(alias="X-Student-Id", min_length=1)]
