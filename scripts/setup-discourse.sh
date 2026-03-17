#!/bin/bash
# ============================================================
# Chronopoli – Discourse Setup Script
# Installs and configures Discourse as the community platform.
# Run ON the EC2 instance. Requires root/sudo.
# Usage: sudo bash setup-discourse.sh [--env-file /path/to/.env]
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'
log()  { echo -e "${GREEN}[DISCOURSE]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()  { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Load env
for candidate in "${2:-}" "$REPO_DIR/infrastructure/extensions/.env" "/data/chronopoli/extensions.env"; do
  if [[ -n "$candidate" ]] && [[ -f "$candidate" ]]; then
    set -a; source "$candidate"; set +a
    log "Loaded env from: $candidate"
    break
  fi
done

# Validate
for var in DISCOURSE_HOSTNAME DISCOURSE_ADMIN_EMAIL SMTP_HOST SMTP_USERNAME SMTP_PASSWORD DISCOURSE_SSO_SECRET; do
  if [[ -z "${!var:-}" ]]; then
    err "Missing required variable: $var"
  fi
done

# ============================================================
# 1. CLONE DISCOURSE DOCKER
# ============================================================
log "Step 1/4: Setting up Discourse Docker..."

DISCOURSE_DIR="/var/discourse"
if [[ -d "$DISCOURSE_DIR/.git" ]]; then
  log "Discourse Docker already cloned"
else
  mkdir -p "$DISCOURSE_DIR"
  git clone https://github.com/discourse/discourse_docker.git "$DISCOURSE_DIR"
fi

cd "$DISCOURSE_DIR"

# ============================================================
# 2. GENERATE app.yml CONFIG
# ============================================================
log "Step 2/4: Generating Discourse configuration..."

cat > containers/app.yml <<APPYML
templates:
  - "templates/postgres.template.yml"
  - "templates/redis.template.yml"
  - "templates/web.template.yml"
  - "templates/web.ratelimited.template.yml"
  - "templates/web.socketed.template.yml"

# No ports exposed — using unix socket via web.socketed.template.yml
# Nginx reverse-proxies to the socket at /var/discourse/shared/standalone/nginx.http.sock

params:
  db_default_text_search_config: "pg_catalog.english"
  db_shared_buffers: "256MB"
  version: tests-passed

env:
  LC_ALL: en_US.UTF-8
  LANG: en_US.UTF-8
  LANGUAGE: en_US.UTF-8

  DISCOURSE_HOSTNAME: "${DISCOURSE_HOSTNAME}"
  DISCOURSE_DEVELOPER_EMAILS: "${DISCOURSE_ADMIN_EMAIL}"

  # Email via AWS SES
  DISCOURSE_SMTP_ADDRESS: "${SMTP_HOST}"
  DISCOURSE_SMTP_PORT: ${SMTP_PORT}
  DISCOURSE_SMTP_USER_NAME: "${SMTP_USERNAME}"
  DISCOURSE_SMTP_PASSWORD: "${SMTP_PASSWORD}"
  DISCOURSE_SMTP_ENABLE_START_TLS: true
  DISCOURSE_SMTP_DOMAIN: "$(echo ${DISCOURSE_HOSTNAME} | cut -d. -f2-)"
  DISCOURSE_NOTIFICATION_EMAIL: "noreply@$(echo ${DISCOURSE_HOSTNAME} | cut -d. -f2-)"

  # S3 backups
  DISCOURSE_BACKUP_LOCATION: s3
  DISCOURSE_S3_BACKUP_BUCKET: "${S3_BACKUPS_BUCKET:-chronopoli-backups-production}"
  DISCOURSE_S3_REGION: "${AWS_REGION:-me-central-1}"

  # SSO with OpenEdX
  DISCOURSE_ENABLE_SSO: true
  DISCOURSE_SSO_URL: "https://learn.$(echo ${DISCOURSE_HOSTNAME} | cut -d. -f2-)/auth/discourse/sso"
  DISCOURSE_SSO_SECRET: "${DISCOURSE_SSO_SECRET}"

volumes:
  - volume:
      host: /var/discourse/shared/standalone
      guest: /shared
  - volume:
      host: /var/discourse/shared/standalone/log/var-log
      guest: /var/log
APPYML

log "app.yml generated ✓"

# ============================================================
# 3. BOOTSTRAP & START
# ============================================================
log "Step 3/4: Bootstrapping Discourse (this takes 10-15 minutes)..."

./launcher bootstrap app
./launcher start app

log "Discourse started ✓"

# ============================================================
# 4. VERIFY
# ============================================================
log "Step 4/4: Verifying..."

sleep 10
if curl -sf -o /dev/null "http://localhost:80"; then
  log "Discourse responding on port 80 ✓"
else
  warn "Discourse not yet responding — may still be starting up"
  warn "Check: ./launcher logs app"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  DISCOURSE SETUP COMPLETE ✓                              ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║                                                          ║"
echo "║  URL:  https://${DISCOURSE_HOSTNAME}                    "
echo "║  SSL:  Let's Encrypt (auto-provisioned)                  ║"
echo "║  SSO:  Wired to OpenEdX (learn.chronopoli.io)           ║"
echo "║                                                          ║"
echo "║  NEXT STEPS:                                             ║"
echo "║  1. Visit https://${DISCOURSE_HOSTNAME}/finish-installation"
echo "║  2. Complete the setup wizard as admin                   ║"
echo "║  3. Run: bash setup-discourse-categories.sh              ║"
echo "║  4. Generate API key in Admin → API                      ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
