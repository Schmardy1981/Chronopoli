#!/bin/bash
# ============================================================
# Chronopoli – Presenton Setup Script
# Installs Presenton AI presentation builder.
# Usage: bash setup-presenton.sh [--env-file /path/to/.env]
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'
log()  { echo -e "${GREEN}[PRESENTON]${NC} $1"; }
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
for var in ANTHROPIC_API_KEY PEXELS_API_KEY; do
  if [[ -z "${!var:-}" ]]; then
    err "Missing required variable: $var"
  fi
done

# ============================================================
# 1. START PRESENTON VIA DOCKER COMPOSE
# ============================================================
log "Step 1/3: Starting Presenton..."

EXTENSIONS_DIR="$REPO_DIR/infrastructure/extensions"
cd "$EXTENSIONS_DIR"

docker compose --env-file .env up -d presenton

log "Presenton container starting..."

# ============================================================
# 2. WAIT FOR STARTUP
# ============================================================
log "Step 2/3: Waiting for Presenton to start..."

MAX_WAIT=60
ELAPSED=0
while [[ $ELAPSED -lt $MAX_WAIT ]]; do
  if curl -sf -o /dev/null "http://localhost:5050/" 2>/dev/null; then
    log "Presenton is running ✓"
    break
  fi
  sleep 5
  ELAPSED=$((ELAPSED + 5))
  echo -n "."
done
echo ""

if [[ $ELAPSED -ge $MAX_WAIT ]]; then
  warn "Presenton did not start in ${MAX_WAIT}s"
  warn "Check: docker compose logs presenton"
fi

# ============================================================
# 3. SETUP BASIC AUTH FOR NGINX
# ============================================================
log "Step 3/3: Setting up access control..."

if command -v htpasswd &>/dev/null; then
  HTPASSWD_FILE="/etc/nginx/.presenton_htpasswd"
  if [[ ! -f "$HTPASSWD_FILE" ]]; then
    log "Creating basic auth file for staff access..."
    echo "Enter a password for the 'chronopoli-staff' user:"
    sudo htpasswd -c "$HTPASSWD_FILE" chronopoli-staff
    log "Basic auth file created at $HTPASSWD_FILE ✓"
  else
    log "Basic auth file already exists ✓"
  fi
else
  warn "htpasswd not found — install: sudo apt install apache2-utils"
  warn "Then run: sudo htpasswd -c /etc/nginx/.presenton_htpasswd chronopoli-staff"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  PRESENTON SETUP COMPLETE ✓                              ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║                                                          ║"
echo "║  URL:     https://slides.${CHRONOPOLI_DOMAIN:-chronopoli.io}"
echo "║  Access:  Staff only (basic auth)                        ║"
echo "║  LLM:     Claude Sonnet 4.6 (Anthropic)                 ║"
echo "║  Images:  Pexels (professional stock)                    ║"
echo "║                                                          ║"
echo "║  NEXT: Configure Nginx reverse proxy (see handbook)      ║"
echo "║  THEN: Upload chronopoli-master.pptx brand template     ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
