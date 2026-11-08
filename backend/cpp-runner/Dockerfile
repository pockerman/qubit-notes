# The sandbox a student's C++ program runs in (backend/src/qubit_notes/domain/programs.py): make cpp-runner
#
# g++ and the standard library only. A program is compiled and run as an unprivileged user; the limits on it are set by
# `docker run`, and its time is for both.
FROM alpine:3.20

RUN apk add --no-cache g++ \
    && mkdir -p /sandbox && chown 10001:10001 /sandbox

ENV HOME=/sandbox
USER 10001:10001
WORKDIR /sandbox
