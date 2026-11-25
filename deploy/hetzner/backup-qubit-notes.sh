#!/bin/bash
# Backs the app's database up, every night (qubit-notes-backup.timer), to the volume, keeping the last ${backup_days}
# days. The students' uploads are on the volume already. A Terraform template.
set -euo pipefail

backups=/srv/qubit-notes/backups
file="$backups/qubit-notes-$(date --utc +%Y-%m-%dT%H%M%SZ).dump"

docker compose --project-directory /opt/qubit-notes --env-file /srv/qubit-notes/secrets.env \
  exec -T db pg_dump --username qubit --format custom qubit_notes > "$file.partial"
mv "$file.partial" "$file"
find "$backups" -name 'qubit-notes-*.dump' -mtime +${backup_days} -delete
