#!/bin/bash
# Runs the app on its server: qubit-notes.service runs it, and runs it again whenever it stops. The operator restarts
# it to take new settings, e.g. a new image_tag or gogi's key: sudo systemctl restart qubit-notes
#
# It reads the app's settings and secrets, writes them for the container, and runs the image on port 80. A Terraform
# template: Terraform fills in what's in $${...}.
set -euo pipefail

export AWS_REGION="${region}"
cd /opt/qubit-notes

settings="$(aws ssm get-parameter --name "${settings}" --query Parameter.Value --output text)"
setting() {
  jq -r ".$1" <<<"$settings"
}
secret() {
  aws secretsmanager get-secret-value --secret-id "$1" --query SecretString --output text
}

database="$(secret "$(setting database)")"
field() {
  jq -r ".$1" <<<"$database"
}

umask 077
{
  jq -r '.environment | to_entries[] | "\(.key)=\(.value)"' <<<"$settings"
  echo "QUBIT_NOTES_DATABASE_URL=postgresql+psycopg://$(field username):$(field password)@$(field host):$(field port)/$(field dbname)?sslmode=require"
  # until the operator puts the key gogi gave the app, the app runs, and reports gogi as not taking it
  if key="$(secret "$(setting gogi_api_key)" 2>/dev/null)"; then
    echo "QUBIT_NOTES_GOGI_API_KEY=$key"
  fi
} > app.env
umask 022
setting gogi_ca > gogi-ca.pem

# the registry's token, if the operator put one: without it, the image is pulled without signing in
if login="$(secret "$(setting registry)" 2>/dev/null)"; then
  jq -r .token <<<"$login" | docker login "$(setting registry_host)" --username "$(jq -r .username <<<"$login")" --password-stdin
fi

image="$(setting image)"
docker pull --quiet "$image"
docker rm --force qubit-notes >/dev/null 2>&1 || true
exec docker run --name qubit-notes --rm \
  --publish 80:8000 \
  --env-file app.env \
  --volume /opt/qubit-notes/gogi-ca.pem:/etc/qubit-notes/gogi-ca.pem:ro \
  --log-driver json-file --log-opt max-size=10m --log-opt max-file=5 \
  "$image"
