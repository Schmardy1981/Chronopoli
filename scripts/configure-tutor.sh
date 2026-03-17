#!/bin/bash
# ============================================================
# Chronopoli – Tutor Configuration Script
# Wires Tutor to AWS services (RDS, S3, SES, Redis)
# Usage: bash configure-tutor.sh [--env-file /path/to/production.env]
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="${1:---env-file}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log()  { echo -e "${GREEN}[CONFIG]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()  { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }

# ============================================================
# LOAD ENVIRONMENT
# ============================================================

# Check for env file argument
if [[ "$1" == "--env-file" ]] && [[ -n "${2:-}" ]]; then
  ENV_FILE="$2"
elif [[ -f "$REPO_DIR/infrastructure/production.env" ]]; then
  ENV_FILE="$REPO_DIR/infrastructure/production.env"
elif [[ -f "/data/chronopoli/production.env" ]]; then
  ENV_FILE="/data/chronopoli/production.env"
else
  err "No environment file found. Copy production.env.template and fill in values:
  cp $REPO_DIR/infrastructure/production.env.template /data/chronopoli/production.env
  nano /data/chronopoli/production.env"
fi

log "Loading environment from: $ENV_FILE"
set -a
source "$ENV_FILE"
set +a

# ============================================================
# VALIDATE REQUIRED VARIABLES
# ============================================================
log "Validating environment variables..."

REQUIRED_VARS=(
  "CHRONOPOLI_DOMAIN"
  "CHRONOPOLI_LMS_HOST"
  "CHRONOPOLI_CMS_HOST"
  "MYSQL_HOST"
  "MYSQL_PORT"
  "MYSQL_ROOT_PASSWORD"
  "S3_MEDIA_BUCKET"
  "S3_STATIC_BUCKET"
  "S3_BACKUPS_BUCKET"
  "AWS_REGION"
  "ADMIN_EMAIL"
)

MISSING=0
for var in "${REQUIRED_VARS[@]}"; do
  if [[ -z "${!var:-}" ]]; then
    warn "Missing required variable: $var"
    MISSING=$((MISSING + 1))
  fi
done

if [[ $MISSING -gt 0 ]]; then
  err "$MISSING required variables missing. Edit $ENV_FILE and try again."
fi

log "All required variables present ✓"

# ============================================================
# SET TUTOR ROOT
# ============================================================
export TUTOR_ROOT="${TUTOR_ROOT:-/data/tutor}"
mkdir -p "$TUTOR_ROOT"

log "Tutor root: $TUTOR_ROOT"

# ============================================================
# CONFIGURE TUTOR
# ============================================================
log "Configuring Tutor..."

# Platform identity
tutor config save \
  --set "PLATFORM_NAME=Chronopoli" \
  --set "LMS_HOST=${CHRONOPOLI_LMS_HOST}" \
  --set "CMS_HOST=${CHRONOPOLI_CMS_HOST}" \
  --set "CONTACT_EMAIL=${ADMIN_EMAIL}" \
  --set "DEFAULT_FROM_EMAIL=noreply@${CHRONOPOLI_DOMAIN}" \
  --set "ENABLE_HTTPS=true" \
  --set "LANGUAGE_CODE=en"

log "Platform identity configured ✓"

# ============================================================
# EXTERNAL MYSQL (RDS)
# ============================================================
log "Wiring external MySQL (RDS)..."

tutor config save \
  --set "RUN_MYSQL=false" \
  --set "MYSQL_HOST=${MYSQL_HOST}" \
  --set "MYSQL_PORT=${MYSQL_PORT}" \
  --set "MYSQL_ROOT_USERNAME=${MYSQL_ROOT_USERNAME:-admin}" \
  --set "MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}"

log "RDS MySQL configured: ${MYSQL_HOST}:${MYSQL_PORT} ✓"

# ============================================================
# EXTERNAL REDIS (ElastiCache) — Optional
# ============================================================
if [[ -n "${REDIS_HOST:-}" ]]; then
  log "Wiring external Redis (ElastiCache)..."
  tutor config save \
    --set "RUN_REDIS=false" \
    --set "REDIS_HOST=${REDIS_HOST}" \
    --set "REDIS_PORT=${REDIS_PORT:-6379}"
  log "ElastiCache Redis configured: ${REDIS_HOST} ✓"
else
  info "No REDIS_HOST set — using Tutor's built-in Redis container"
  tutor config save --set "RUN_REDIS=true"
fi

# ============================================================
# S3 STORAGE
# ============================================================
log "Configuring S3 storage..."

# For IAM role-based access (recommended), we don't set access keys.
# The EC2 instance profile provides credentials automatically.
tutor config save \
  --set "OPENEDX_AWS_ACCESS_KEY=${AWS_ACCESS_KEY_ID:-}" \
  --set "OPENEDX_AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-}"

# S3 bucket configuration is injected via the Chronopoli Tutor plugin's
# LMS settings patch. We store the values for the plugin to consume.
cat > "$TUTOR_ROOT/env/plugins/chronopoli/s3-config.env" 2>/dev/null || true

log "S3 buckets: media=${S3_MEDIA_BUCKET}, static=${S3_STATIC_BUCKET} ✓"

# ============================================================
# EMAIL (AWS SES)
# ============================================================
if [[ -n "${SMTP_HOST:-}" ]]; then
  log "Configuring AWS SES email..."
  tutor config save \
    --set "RUN_SMTP=false" \
    --set "SMTP_HOST=${SMTP_HOST}" \
    --set "SMTP_PORT=${SMTP_PORT:-587}" \
    --set "SMTP_USE_TLS=true" \
    --set "SMTP_USERNAME=${SMTP_USERNAME:-}" \
    --set "SMTP_PASSWORD=${SMTP_PASSWORD:-}"
  log "SES email configured: ${SMTP_HOST} ✓"
else
  info "No SMTP_HOST set — using Tutor's built-in SMTP container"
  tutor config save --set "RUN_SMTP=true"
fi

# ============================================================
# THEME
# ============================================================
log "Configuring Chronopoli theme..."
tutor config save \
  --set "OPENEDX_THEME=chronopoli-theme"

# ============================================================
# INSTALL CHRONOPOLI TUTOR PLUGIN
# ============================================================
log "Installing Chronopoli Tutor plugin..."

PLUGIN_DIR="$REPO_DIR/tutor/plugins/chronopoli"
if [[ -d "$PLUGIN_DIR" ]]; then
  # Activate the same venv where Tutor is installed
  VENV_DIR="/opt/chronopoli/venv"
  if [[ -f "$VENV_DIR/bin/activate" ]]; then
    source "$VENV_DIR/bin/activate"
  fi

  pip install -e "$PLUGIN_DIR" --quiet
  tutor plugins enable chronopoli
  tutor config save

  log "Chronopoli plugin installed and enabled ✓"
else
  warn "Plugin not found at $PLUGIN_DIR — clone the repo first"
fi

# ============================================================
# ENABLE STANDARD PLUGINS
# ============================================================
log "Enabling Tutor plugins..."

for plugin in mfe notes forum; do
  if tutor plugins enable "$plugin" 2>/dev/null; then
    info "  Enabled: $plugin"
  else
    warn "  Plugin not available: $plugin"
  fi
done

tutor config save

# ============================================================
# GENERATE S3 SETTINGS FOR LMS
# ============================================================
log "Generating S3 settings for OpenEdX LMS..."

# Write S3 config that the plugin injects into LMS settings
S3_SETTINGS_FILE="$TUTOR_ROOT/env/plugins/chronopoli/apps/openedx/settings/lms/s3.py"
mkdir -p "$(dirname "$S3_SETTINGS_FILE")" 2>/dev/null || true

cat > "$REPO_DIR/tutor/plugins/chronopoli/tutorchronopoli/patches/openedx-lms-production-settings" <<PATCH
# ============================================================
# CHRONOPOLI PRODUCTION SETTINGS (auto-generated by configure-tutor.sh)
# ============================================================

# S3 Storage
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_STORAGE_BUCKET_NAME = "${S3_MEDIA_BUCKET}"
AWS_S3_CUSTOM_DOMAIN = "${S3_MEDIA_BUCKET}.s3.${AWS_REGION}.amazonaws.com"
AWS_S3_REGION_NAME = "${AWS_REGION}"
AWS_DEFAULT_ACL = "public-read"
AWS_QUERYSTRING_AUTH = False

# Static files on S3
STATICFILES_STORAGE = "storages.backends.s3boto3.S3StaticStorage"
AWS_STATIC_BUCKET_NAME = "${S3_STATIC_BUCKET}"

# Media file upload
FILE_UPLOAD_STORAGE_BUCKET_NAME = "${S3_MEDIA_BUCKET}"
VIDEO_UPLOAD_PIPELINE = {
    "VEM_S3_BUCKET": "${S3_MEDIA_BUCKET}",
}

# Course import/export storage
COURSE_IMPORT_EXPORT_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# Grades download
GRADES_DOWNLOAD = {
    "STORAGE_TYPE": "S3",
    "BUCKET": "${S3_MEDIA_BUCKET}",
    "ROOT_PATH": "grades",
}
PATCH

log "S3 LMS settings written ✓"

# ============================================================
# SUMMARY
# ============================================================
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  CHRONOPOLI TUTOR CONFIGURATION COMPLETE ✓               ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║                                                          ║"
echo "║  LMS:      https://${CHRONOPOLI_LMS_HOST}               "
echo "║  Studio:   https://${CHRONOPOLI_CMS_HOST}               "
echo "║  Database:  ${MYSQL_HOST}:${MYSQL_PORT}                 "
if [[ -n "${REDIS_HOST:-}" ]]; then
echo "║  Redis:     ${REDIS_HOST}                               "
else
echo "║  Redis:     Docker container (built-in)                  ║"
fi
if [[ -n "${SMTP_HOST:-}" ]]; then
echo "║  Email:     ${SMTP_HOST} (SES)                          "
else
echo "║  Email:     Docker container (built-in)                  ║"
fi
echo "║  S3 Media:  ${S3_MEDIA_BUCKET}                          "
echo "║  S3 Static: ${S3_STATIC_BUCKET}                         "
echo "║                                                          ║"
echo "║  NEXT STEPS:                                             ║"
echo "║  1. tutor images build openedx     (10-20 min)          ║"
echo "║  2. tutor local start -d                                 ║"
echo "║  3. tutor local do init                                  ║"
echo "║  4. bash setup-districts.sh                              ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
