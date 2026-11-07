# The sandbox a student's Go program runs in (backend/src/qubit_notes/domain/go_programs.py): make go-runner
#
# The standard library is compiled here, into the cache a program is built with, or every run would compile it again,
# which takes more than ten seconds. Programs run as an unprivileged user; the limits on them are set by `docker run`.
FROM golang:1.25-alpine

ENV CGO_ENABLED=0 GOPROXY=off GOTOOLCHAIN=local GOCACHE=/sandbox/cache GOPATH=/sandbox/go HOME=/sandbox

RUN mkdir -p /sandbox/cache /sandbox/go \
    && go build std \
    && chown -R 10001:10001 /sandbox

USER 10001:10001
WORKDIR /sandbox
