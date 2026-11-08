# The sandbox a student's SQL runs in (backend/src/qubit_notes/domain/programs.py): make sql-runner
#
# SQLite, on a database of its own in memory, thrown away with the container. It is run with -safe, so that nothing
# typed can reach files or a shell: no .shell, .system, .output, .import, ATTACH, readfile() or writefile(). It runs as
# an unprivileged user; the limits on it are set by `docker run`.
FROM alpine:3.20

RUN apk add --no-cache sqlite \
    && mkdir -p /sandbox && chown 10001:10001 /sandbox

ENV HOME=/sandbox
USER 10001:10001
WORKDIR /sandbox
