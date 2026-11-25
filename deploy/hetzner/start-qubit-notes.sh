#!/bin/bash
# Runs the app, its Postgres and Caddy on the server: qubit-notes.service runs it, and runs it again whenever it stops.
# The operator restarts it to take new keys (keys.env): sudo systemctl restart qubit-notes
#
# The first time it runs on the volume, it makes the app's secrets there, so they're never in Terraform's state: the
# database's password, and the secret the app keeps the keys and tokens it is given with.
set -euo pipefail

data=/srv/qubit-notes

# the volume is attached once the server is up, so it may not be there yet: the service tries again
if ! mountpoint --quiet "$data"; then
  mount "$data" || { echo "the volume isn't attached yet" >&2; exit 1; }
fi

mkdir -p "$data/postgres" "$data/material" "$data/caddy/data" "$data/caddy/config" "$data/backups" "$data/docker"
# the app's image runs as qubit (uid 10001)
chown 10001 "$data/material"

if [ ! -f "$data/secrets.env" ]; then
  umask 077
  {
    echo "POSTGRES_PASSWORD=$(openssl rand -hex 32)"
    echo "QUBIT_NOTES_SECRET_KEY=$(openssl rand -hex 32)"
  } > "$data/secrets.env.new"
  mv "$data/secrets.env.new" "$data/secrets.env"
  umask 022
fi

# where the operator logs in to the image's registry, if it's private, so a new server keeps the login:
#   sudo DOCKER_CONFIG=/srv/qubit-notes/docker docker login ghcr.io
export DOCKER_CONFIG="$data/docker"

compose=(docker compose --project-directory /opt/qubit-notes --env-file "$data/secrets.env")
"${compose[@]}" pull --quiet
exec "${compose[@]}" up --remove-orphans
