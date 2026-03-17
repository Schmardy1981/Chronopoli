#!/bin/bash
# ============================================================
# Chronopoli – Deployment Script
# Usage: ./scripts/deploy.sh --environment [production|staging]
# ============================================================

set -euo pipefail

# ============================================================
# CONFIGURATION
# ============================================================
ENVIRONMENT=${1:-staging}
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TUTOR_ROOT="${HOME}/.local/share/tutor"
LOG_FILE="/var/log/chronopoli-deploy.log"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================
# HELPERS
# ============================================================
log() {
  echo -e "${GREEN}[CHRONOPOLI]${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
  echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
  echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
  exit 1
}

info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

# ============================================================
# PRE-FLIGHT CHECKS
# ============================================================
preflight_checks() {
  log "Running pre-flight checks..."

  # Check Docker
  if ! command -v docker &> /dev/null; then
    error "Docker is not installed. Run: sudo apt-get install docker.io"
  fi
  
  # Check Tutor
  if ! command -v tutor &> /dev/null; then
    error "Tutor is not installed. Run: pip install tutor[full]"
  fi

  # Check environment
  if [[ "$ENVIRONMENT" != "production" && "$ENVIRONMENT" != "staging" ]]; then
    error "Invalid environment: $ENVIRONMENT. Use 'production' or 'staging'"
  fi
  
  log "Pre-flight checks passed ✓"
}

# ============================================================
# ENVIRONMENT SETUP
# ============================================================
setup_environment() {
  log "Setting up $ENVIRONMENT environment..."
  
  ENV_FILE="${REPO_DIR}/infrastructure/${ENVIRONMENT}.env"
  
  if [[ ! -f "$ENV_FILE" ]]; then
    warn "No environment file found at $ENV_FILE"
    warn "Copy infrastructure/staging.env.example to infrastructure/${ENVIRONMENT}.env and fill in values"
  fi
  
  # Copy Tutor config
  if [[ -f "${REPO_DIR}/tutor/config.yml" ]]; then
    cp "${REPO_DIR}/tutor/config.yml" "${TUTOR_ROOT}/config.yml"
    log "Tutor config deployed ✓"
  fi
}

# ============================================================
# INSTALL PLUGINS
# ============================================================
install_plugins() {
  log "Installing Chronopoli plugins..."
  
  # Core Tutor plugins
  tutor plugins enable mfe
  tutor plugins enable indigo
  tutor plugins enable notes
  tutor plugins enable forum
  
  # Install our custom plugins
  PLUGIN_DIR="${REPO_DIR}/tutor/plugins/chronopoli"
  if [[ -d "$PLUGIN_DIR" ]]; then
    pip install -e "$PLUGIN_DIR" --quiet
    tutor plugins enable chronopoli
    log "Chronopoli plugin installed ✓"
  fi
  
  tutor config save
  log "Plugins installed ✓"
}

# ============================================================
# DEPLOY THEME
# ============================================================
deploy_theme() {
  log "Deploying Chronopoli theme..."
  
  THEME_SRC="${REPO_DIR}/theme/chronopoli-theme"
  THEME_DEST="${TUTOR_ROOT}/env/build/openedx/themes/chronopoli-theme"
  
  if [[ -d "$THEME_SRC" ]]; then
    mkdir -p "${TUTOR_ROOT}/env/build/openedx/themes/"
    cp -r "$THEME_SRC" "$THEME_DEST"
    log "Theme files deployed ✓"
  else
    warn "Theme directory not found at $THEME_SRC"
  fi
}

# ============================================================
# BUILD & LAUNCH
# ============================================================
build_and_launch() {
  log "Building OpenEdX Docker images..."
  log "(This takes 10–20 minutes on first run)"
  
  tutor images build openedx
  
  log "Starting Chronopoli platform..."
  tutor local start -d
  
  # Wait for services to be ready
  log "Waiting for services to start (60 seconds)..."
  sleep 60
  
  # Health check
  LMS_HOST=$(tutor config printvalue LMS_HOST)
  if curl -sf "https://${LMS_HOST}/heartbeat" > /dev/null 2>&1; then
    log "LMS health check passed ✓"
  else
    warn "LMS health check failed. Check logs: tutor local logs lms"
  fi
}

# ============================================================
# INIT (first deployment only)
# ============================================================
init_platform() {
  log "Initializing databases (first deployment)..."
  
  tutor local do init
  
  log "Creating admin user..."
  read -p "Admin username [admin]: " ADMIN_USER
  ADMIN_USER=${ADMIN_USER:-admin}
  read -p "Admin email: " ADMIN_EMAIL
  read -s -p "Admin password: " ADMIN_PASS
  echo ""
  
  tutor local do createuser \
    --superuser \
    --staff \
    --password "$ADMIN_PASS" \
    "$ADMIN_USER" "$ADMIN_EMAIL"
  
  log "Platform initialized ✓"
  
  # Enable Chronopoli theme
  tutor local do settheme chronopoli-theme
  log "Chronopoli theme enabled ✓"
}

# ============================================================
# BACKUP (before updates)
# ============================================================
backup() {
  log "Creating backup before deployment..."
  
  BACKUP_DIR="/var/backups/chronopoli"
  mkdir -p "$BACKUP_DIR"
  
  BACKUP_FILE="${BACKUP_DIR}/backup-${TIMESTAMP//[: ]/-}.sql.gz"
  
  tutor local do exec mysql mysqldump -u root \
    --password="$(tutor config printvalue MYSQL_ROOT_PASSWORD)" \
    openedx | gzip > "$BACKUP_FILE"
  
  log "Backup saved to: $BACKUP_FILE ✓"
}

# ============================================================
# MAIN
# ============================================================
main() {
  echo ""
  echo "╔══════════════════════════════════════════════════════╗"
  echo "║         CHRONOPOLI DEPLOYMENT SCRIPT                 ║"
  echo "║         Environment: ${ENVIRONMENT^^}                          ║"
  echo "║         Timestamp: $TIMESTAMP          ║"
  echo "╚══════════════════════════════════════════════════════╝"
  echo ""
  
  preflight_checks
  setup_environment
  install_plugins
  deploy_theme
  
  # Check if this is first deployment
  if [[ ! -f "${TUTOR_ROOT}/.initialized" ]]; then
    log "First deployment detected – running initialization..."
    build_and_launch
    init_platform
    touch "${TUTOR_ROOT}/.initialized"
  else
    log "Updating existing deployment..."
    backup
    build_and_launch
  fi
  
  echo ""
  log "╔══════════════════════════════════════════════════════╗"
  log "║  CHRONOPOLI DEPLOYMENT COMPLETE ✓                   ║"
  log "║                                                      ║"
  LMS_HOST=$(tutor config printvalue LMS_HOST 2>/dev/null || echo "learn.chronopoli.io")
  CMS_HOST=$(tutor config printvalue CMS_HOST 2>/dev/null || echo "studio.chronopoli.io")
  log "║  LMS:    https://${LMS_HOST}"
  log "║  Studio: https://${CMS_HOST}"
  log "║  Admin:  https://${LMS_HOST}/admin"
  log "╚══════════════════════════════════════════════════════╝"
  echo ""
}

# Handle flags
case "${1:-}" in
  --help|-h)
    echo "Usage: ./scripts/deploy.sh [production|staging]"
    echo ""
    echo "Commands:"
    echo "  production   Deploy to production AWS"
    echo "  staging      Deploy to staging server"
    echo "  --backup     Run backup only"
    echo "  --init       Re-initialize (WARNING: deletes data)"
    exit 0
    ;;
  --backup)
    backup
    exit 0
    ;;
  --init)
    init_platform
    exit 0
    ;;
  *)
    main
    ;;
esac
