from typing import Annotated

from fastapi import Header, Request

from study_assistant.domain.courses import Courses
from study_assistant.domain.materials import Materials
from study_assistant.domain.notes import Notes
from study_assistant.domain.quizzes import Quizzes
from study_assistant.domain.reading import Reading
from study_assistant.domain.summaries import Summaries


def courses(request: Request) -> Courses:
    return request.app.state.courses


def materials(request: Request) -> Materials:
    return request.app.state.materials


def reading(request: Request) -> Reading:
    return request.app.state.reading


def notes(request: Request) -> Notes:
    return request.app.state.notes


def summaries(request: Request) -> Summaries:
    return request.app.state.summaries


def quizzes(request: Request) -> Quizzes:
    return request.app.state.quizzes


# the student making the request. There is no authentication yet: the client says who it is
Student = Annotated[str, Header(alias="X-Student-Id", min_length=1)]
