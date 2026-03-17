#!/bin/bash
# ============================================================
# Chronopoli – Opencast Setup Script
# Installs Opencast video management platform.
# Usage: bash setup-opencast.sh [--env-file /path/to/.env]
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'
log()  { echo -e "${GREEN}[OPENCAST]${NC} $1"; }
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
for var in MYSQL_HOST MYSQL_ROOT_PASSWORD OPENCAST_ADMIN_PASS S3_OPENCAST_BUCKET; do
  if [[ -z "${!var:-}" ]]; then
    err "Missing required variable: $var"
  fi
done

# ============================================================
# 1. CREATE OPENCAST DATABASE ON RDS
# ============================================================
log "Step 1/4: Creating Opencast database on RDS..."

mysql -h "${MYSQL_HOST}" -P "${MYSQL_PORT:-3306}" \
  -u "${MYSQL_ROOT_USERNAME:-admin}" -p"${MYSQL_ROOT_PASSWORD}" \
  -e "CREATE DATABASE IF NOT EXISTS opencast CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null && \
  log "Database 'opencast' ready ✓" || \
  warn "Could not create database — may already exist or MySQL client not installed"

# ============================================================
# 2. START OPENCAST VIA DOCKER COMPOSE
# ============================================================
log "Step 2/4: Starting Opencast..."

EXTENSIONS_DIR="$REPO_DIR/infrastructure/extensions"
cd "$EXTENSIONS_DIR"

# Start only Opencast
docker compose --env-file .env up -d opencast

log "Opencast container starting..."

# ============================================================
# 3. WAIT FOR STARTUP
# ============================================================
log "Step 3/4: Waiting for Opencast to initialize (this takes 3-5 minutes)..."

MAX_WAIT=300
ELAPSED=0
while [[ $ELAPSED -lt $MAX_WAIT ]]; do
  if curl -sf -o /dev/null "http://localhost:8080/info/health" 2>/dev/null; then
    log "Opencast is healthy ✓"
    break
  fi
  sleep 10
  ELAPSED=$((ELAPSED + 10))
  echo -n "."
done
echo ""

if [[ $ELAPSED -ge $MAX_WAIT ]]; then
  warn "Opencast did not become healthy in ${MAX_WAIT}s"
  warn "Check: docker compose logs opencast"
fi

# ============================================================
# 4. CONFIGURE LTI FOR OPENEDX
# ============================================================
log "Step 4/4: Configuring LTI integration..."

log "LTI Consumer Key:    ${OPENCAST_LTI_KEY:-chronopoli-openedx}"
log "LTI Consumer Secret: (set in extensions .env)"
log ""
log "To complete LTI setup in Opencast:"
log "  1. Login at https://video.${CHRONOPOLI_DOMAIN:-chronopoli.io}/admin-ng"
log "  2. Go to Configuration → LTI"
log "  3. Set Consumer Key: ${OPENCAST_LTI_KEY:-chronopoli-openedx}"
log "  4. Set Consumer Secret: (your OPENCAST_LTI_SECRET value)"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  OPENCAST SETUP COMPLETE ✓                               ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║                                                          ║"
echo "║  Admin:    https://video.${CHRONOPOLI_DOMAIN:-chronopoli.io}/admin-ng"
echo "║  User:     admin                                         ║"
echo "║  S3:       ${S3_OPENCAST_BUCKET}                        "
echo "║  Database: opencast @ ${MYSQL_HOST}                     "
echo "║                                                          ║"
echo "║  NEXT: Configure Nginx reverse proxy (see handbook)      ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
