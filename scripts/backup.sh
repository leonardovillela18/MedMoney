#!/bin/sh
set -eu
: "${DATABASE_URL:?DATABASE_URL is required}"
mkdir -p "${BACKUP_DIR:-./backups}"
stamp=$(date +%Y%m%d-%H%M%S)
pg_dump --format=custom --no-owner --dbname="$DATABASE_URL" --file="${BACKUP_DIR:-./backups}/medmoney-$stamp.dump"
find "${BACKUP_DIR:-./backups}" -name 'medmoney-*.dump' -mtime +"${BACKUP_RETENTION_DAYS:-14}" -delete
