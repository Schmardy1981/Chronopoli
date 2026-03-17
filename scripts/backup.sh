#!/bin/bash
# ============================================================
# Chronopoli – Automated Backup Script
# Backs up MySQL database and media files to S3.
# Usage: bash backup.sh [--full]
# Schedule via cron: 0 3 * * * /opt/chronopoli/repo/scripts/backup.sh
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
BACKUP_DIR="/data/backups"
LOG_FILE="/var/log/chronopoli-backup.log"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${GREEN}[BACKUP]${NC} $(date '+%H:%M:%S') $1" | tee -a "$LOG_FILE"; }
err()  { echo -e "${RED}[ERROR]${NC} $(date '+%H:%M:%S') $1" | tee -a "$LOG_FILE"; exit 1; }
warn() { echo -e "${YELLOW}[WARN]${NC} $(date '+%H:%M:%S') $1" | tee -a "$LOG_FILE"; }

# Load env
for candidate in "$REPO_DIR/infrastructure/production.env" "/data/chronopoli/production.env"; do
  if [[ -f "$candidate" ]]; then
    set -a; source "$candidate"; set +a
    break
  fi
done

export TUTOR_ROOT="${TUTOR_ROOT:-/data/tutor}"
S3_BUCKET="${S3_BACKUPS_BUCKET:-chronopoli-backups-production}"
FULL_BACKUP="${1:-}"

mkdir -p "$BACKUP_DIR"

log "Starting backup — $TIMESTAMP"

# ============================================================
# 1. DATABASE BACKUP
# ============================================================
log "Backing up MySQL database..."

DB_FILE="$BACKUP_DIR/db-${TIMESTAMP}.sql.gz"
MYSQL_PASS=$(tutor config printvalue MYSQL_ROOT_PASSWORD 2>/dev/null || echo "${MYSQL_ROOT_PASSWORD:-}")

if [[ -z "$MYSQL_PASS" ]]; then
  err "Cannot determine MySQL password"
fi

# Use tutor exec to run mysqldump inside the container (or against RDS)
tutor local do exec lms python manage.py lms shell -c "
import subprocess, sys
from django.conf import settings
db = settings.DATABASES['default']
cmd = [
    'mysqldump',
    '-h', db['HOST'],
    '-P', str(db['PORT']),
    '-u', db['USER'],
    f\"--password={db['PASSWORD']}\",
    '--single-transaction',
    '--routines',
    '--triggers',
    db['NAME'],
]
result = subprocess.run(cmd, capture_output=True)
if result.returncode == 0:
    sys.stdout.buffer.write(result.stdout)
else:
    print(f'ERROR: {result.stderr.decode()}', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null | gzip > "$DB_FILE"

DB_SIZE=$(du -sh "$DB_FILE" 2>/dev/null | awk '{print $1}')
log "Database backup: $DB_FILE ($DB_SIZE) ✓"

# ============================================================
# 2. TUTOR CONFIG BACKUP
# ============================================================
log "Backing up Tutor config..."

CONFIG_FILE="$BACKUP_DIR/tutor-config-${TIMESTAMP}.tar.gz"
tar -czf "$CONFIG_FILE" -C "$TUTOR_ROOT" config.yml 2>/dev/null || \
  warn "Could not backup tutor config"

log "Config backup ✓"

# ============================================================
# 3. MEDIA FILES (only on --full)
# ============================================================
if [[ "$FULL_BACKUP" == "--full" ]]; then
  log "Full backup: Backing up media files..."
  MEDIA_FILE="$BACKUP_DIR/media-${TIMESTAMP}.tar.gz"

  # Tutor stores media in Docker volumes
  MEDIA_PATH=$(docker volume inspect tutor_local_data 2>/dev/null | jq -r '.[0].Mountpoint' || echo "")

  if [[ -n "$MEDIA_PATH" ]] && [[ -d "$MEDIA_PATH" ]]; then
    tar -czf "$MEDIA_FILE" -C "$MEDIA_PATH" . 2>/dev/null || \
      warn "Media backup failed"
    MEDIA_SIZE=$(du -sh "$MEDIA_FILE" 2>/dev/null | awk '{print $1}')
    log "Media backup: $MEDIA_FILE ($MEDIA_SIZE) ✓"
  else
    warn "Media volume not found — skipping"
  fi
fi

# ============================================================
# 4. UPLOAD TO S3
# ============================================================
log "Uploading backups to S3..."

aws s3 cp "$DB_FILE" "s3://${S3_BUCKET}/db/" --quiet && \
  log "Uploaded: db-${TIMESTAMP}.sql.gz → s3://${S3_BUCKET}/db/ ✓" || \
  warn "S3 upload failed for database backup"

aws s3 cp "$CONFIG_FILE" "s3://${S3_BUCKET}/config/" --quiet && \
  log "Uploaded: tutor-config → s3://${S3_BUCKET}/config/ ✓" || \
  warn "S3 upload failed for config backup"

if [[ "$FULL_BACKUP" == "--full" ]] && [[ -f "${MEDIA_FILE:-}" ]]; then
  aws s3 cp "$MEDIA_FILE" "s3://${S3_BUCKET}/media/" --quiet && \
    log "Uploaded: media → s3://${S3_BUCKET}/media/ ✓" || \
    warn "S3 upload failed for media backup"
fi

# ============================================================
# 5. CLEANUP OLD LOCAL BACKUPS (keep last 7 days)
# ============================================================
log "Cleaning up local backups older than 7 days..."
find "$BACKUP_DIR" -name "*.gz" -mtime +7 -delete 2>/dev/null || true

REMAINING=$(ls -1 "$BACKUP_DIR"/*.gz 2>/dev/null | wc -l)
log "Local backup files: $REMAINING remaining"

# ============================================================
# SUMMARY
# ============================================================
log "Backup complete — $TIMESTAMP"
log "  Database: s3://${S3_BUCKET}/db/db-${TIMESTAMP}.sql.gz"
log "  Config:   s3://${S3_BUCKET}/config/tutor-config-${TIMESTAMP}.tar.gz"
if [[ "$FULL_BACKUP" == "--full" ]]; then
  log "  Media:    s3://${S3_BUCKET}/media/media-${TIMESTAMP}.tar.gz"
fi
