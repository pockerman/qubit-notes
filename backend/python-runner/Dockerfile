# The sandbox a student's Python program runs in (backend/src/qubit_notes/domain/programs.py): make python-runner
#
# Only the standard library: a program has no network, so it can't install anything. Programs run as an unprivileged
# user; the limits on them are set by `docker run`. Output isn't buffered, so what is printed to stdout and stderr
# comes in the order it was printed, and what a program printed before it was stopped isn't lost.
FROM python:3.13-alpine

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 HOME=/sandbox

RUN mkdir -p /sandbox && chown 10001:10001 /sandbox

USER 10001:10001
WORKDIR /sandbox
