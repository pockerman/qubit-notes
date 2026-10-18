from typing import Annotated

from fastapi import Depends, Request

from study_assistant.domain.assistant import Assistant
from study_assistant.domain.courses import Courses
from study_assistant.domain.images import Images
from study_assistant.domain.materials import Materials
from study_assistant.domain.notes import Notes
from study_assistant.domain.quizzes import Quizzes
from study_assistant.domain.reading import Reading
from study_assistant.domain.summaries import Summaries
from study_assistant.domain.topics import Topics


def courses(request: Request) -> Courses:
    return request.app.state.courses


def images(request: Request) -> Images:
    return request.app.state.images


def materials(request: Request) -> Materials:
    return request.app.state.materials


def reading(request: Request) -> Reading:
    return request.app.state.reading


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
