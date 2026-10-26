"""Summaries, quizzes and flashcards, and the reviews of the flashcards. Asking for a summary, a quiz or a deck returns
the newest saved one, or writes one if there's none or the student asks for a new one, so it's a POST."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from qubit_notes.api.deps import Student, flashcards, quizzes, reviews, summaries
from qubit_notes.domain.flashcards import Deck, Flashcards
from qubit_notes.domain.quizzes import Attempt, Quiz, Quizzes
from qubit_notes.domain.reviews import Due, ReviewCard, Reviews
from qubit_notes.domain.sources import Scope
from qubit_notes.domain.summaries import Summaries, Summary

router = APIRouter(tags=["study"])
SummariesDep = Annotated[Summaries, Depends(summaries)]
QuizzesDep = Annotated[Quizzes, Depends(quizzes)]
FlashcardsDep = Annotated[Flashcards, Depends(flashcards)]
ReviewsDep = Annotated[Reviews, Depends(reviews)]


class SummaryRequest(Scope):
    # write a new summary even if one is saved
    new: bool = False


class QuizRequest(Scope):
    questions: int = 5
    new: bool = False


class DeckRequest(Scope):
    cards: int = 10
    new: bool = False


class Remembered(BaseModel):
    # how well the student remembered the card: again, hard, good or easy
    answer: str


class Answers(BaseModel):
    # the index of the chosen choice of each question, or null for one not answered
    answers: list[int | None]


@router.post("/summaries", response_model=Summary)
async def summary(request: SummaryRequest, student: Student, service: SummariesDep) -> Summary:
    scope = Scope(**request.model_dump(exclude={"new"}))
    return await run_in_threadpool(service.get, student, scope, request.new)


@router.get("/summaries", response_model=list[Summary])
async def summaries_of(scope: Annotated[Scope, Query()], student: Student, service: SummariesDep) -> list[Summary]:
    """the student's summaries of the scope, newest first"""
    return await run_in_threadpool(service.history, student, scope)


@router.post("/quizzes", response_model=Quiz)
async def quiz(request: QuizRequest, student: Student, service: QuizzesDep) -> Quiz:
    scope = Scope(**request.model_dump(exclude={"new", "questions"}))
    return await run_in_threadpool(service.get, student, scope, request.questions, request.new)


@router.get("/quizzes", response_model=list[Quiz])
async def quizzes_of(scope: Annotated[Scope, Query()], student: Student, service: QuizzesDep) -> list[Quiz]:
    """the student's quizzes on the scope, newest first"""
    return await run_in_threadpool(service.history, student, scope)


@router.post("/quizzes/{quiz_id}/attempts", response_model=Attempt, status_code=201)
async def take_quiz(quiz_id: str, answers: Answers, student: Student, service: QuizzesDep) -> Attempt:
    return await run_in_threadpool(service.take, student, quiz_id, answers.answers)


@router.get("/quizzes/{quiz_id}/attempts", response_model=list[Attempt])
async def attempts(quiz_id: str, student: Student, service: QuizzesDep) -> list[Attempt]:
    """the student's attempts at the quiz, newest first"""
    return await run_in_threadpool(service.attempts, student, quiz_id)


@router.post("/flashcards", response_model=Deck)
async def deck(request: DeckRequest, student: Student, service: FlashcardsDep) -> Deck:
    scope = Scope(**request.model_dump(exclude={"new", "cards"}))
    return await run_in_threadpool(service.get, student, scope, request.cards, request.new)


@router.get("/flashcards", response_model=list[Deck])
async def decks_of(scope: Annotated[Scope, Query()], student: Student, service: FlashcardsDep) -> list[Deck]:
    """the student's decks of the scope, newest first"""
    return await run_in_threadpool(service.history, student, scope)


@router.get("/reviews", response_model=Due)
async def due(student: Student, service: ReviewsDep, course_id: str | None = None) -> Due:
    """the student's cards due for review, in all their courses or in one, oldest due first"""
    return await run_in_threadpool(service.due, student, course_id)


@router.post("/reviews/{card_id}", response_model=ReviewCard)
async def review(card_id: str, remembered: Remembered, student: Student, service: ReviewsDep) -> ReviewCard:
    return await run_in_threadpool(service.review, student, card_id, remembered.answer)
