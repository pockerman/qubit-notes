from typing import Annotated

from fastapi import Depends, Request

from qubit_notes.domain.app_keys import AppKeys
from qubit_notes.domain.assistant import Assistant
from qubit_notes.domain.conversions import Conversions
from qubit_notes.domain.courses import Courses
from qubit_notes.domain.generating import Generator
from qubit_notes.domain.images import Images
from qubit_notes.domain.materials import Materials
from qubit_notes.domain.notes import Notes
from qubit_notes.domain.quizzes import Quizzes
from qubit_notes.domain.reading import Reading
from qubit_notes.domain.reading_order import ReadingOrder
from qubit_notes.domain.references import References
from qubit_notes.domain.summaries import Summaries
from qubit_notes.domain.topics import Topics


def app_keys(request: Request) -> AppKeys:
    return request.app.state.app_keys


def courses(request: Request) -> Courses:
    return request.app.state.courses


def images(request: Request) -> Images:
    return request.app.state.images


def conversions(request: Request) -> Conversions:
    return request.app.state.conversions


def materials(request: Request) -> Materials:
    return request.app.state.materials


def reading(request: Request) -> Reading:
    return request.app.state.reading


def references(request: Request) -> References:
    return request.app.state.references


def reading_order(request: Request) -> ReadingOrder:
    return request.app.state.reading_order


def generator(request: Request) -> Generator:
    return request.app.state.generator


def notes(request: Request) -> Notes:
    return request.app.state.notes


def topics(request: Request) -> Topics:
    return request.app.state.topics


def summaries(request: Request) -> Summaries:
    return request.app.state.summaries


def quizzes(request: Request) -> Quizzes:
    return request.app.state.quizzes


def assistant(request: Request) -> Assistant:
    return request.app.state.assistant


def current_student(request: Request) -> str:
    return request.app.state.authenticator.student(request)


def student_in_link(request: Request) -> str:
    """the student following a link, e.g. a <video>'s, which can't send headers: who they are is in the link"""
    return request.app.state.authenticator.student(request, in_link=True)


# the student making the request: who they say they are, or who their Cognito token says (see api/auth.py)
Student = Annotated[str, Depends(current_student)]
StudentInLink = Annotated[str, Depends(student_in_link)]
