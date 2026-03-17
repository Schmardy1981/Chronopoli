#!/bin/bash
# ============================================================
# Chronopoli – Server Setup Script
# Run this ON the EC2 instance after SSH-ing in for the first time.
# Usage: sudo bash setup-server.sh
# ============================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log()  { echo -e "${GREEN}[SETUP]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()  { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }

# ============================================================
# 0. PRE-CHECKS
# ============================================================
if [[ $EUID -ne 0 ]]; then
  err "This script must be run as root (use sudo)"
fi

EXPECTED_OS="Ubuntu"
if ! grep -qi "$EXPECTED_OS" /etc/os-release 2>/dev/null; then
  err "This script requires Ubuntu 22.04 LTS"
fi

log "Starting Chronopoli server setup..."
log "$(date '+%Y-%m-%d %H:%M:%S')"

# ============================================================
# 1. SYSTEM UPDATE
# ============================================================
log "Step 1/8: Updating system packages..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get upgrade -y -qq
apt-get install -y -qq \
  curl wget git unzip jq htop tmux \
  python3 python3-pip python3-venv \
  apt-transport-https ca-certificates \
  software-properties-common \
  fail2ban ufw \
  awscli

log "System packages updated ✓"

# ============================================================
# 2. DOCKER
# ============================================================
log "Step 2/8: Installing Docker..."
if command -v docker &>/dev/null; then
  info "Docker already installed: $(docker --version)"
else
  curl -fsSL https://get.docker.com | sh
  systemctl enable docker
  systemctl start docker
  usermod -aG docker ubuntu
fi

# Docker Compose plugin
if ! docker compose version &>/dev/null; then
  apt-get install -y -qq docker-compose-plugin
fi

log "Docker ready: $(docker --version) ✓"

# ============================================================
# 3. DATA VOLUME (EBS /dev/xvdf → /data)
# ============================================================
log "Step 3/8: Mounting data volume..."
DATA_DEVICE="/dev/xvdf"
DATA_MOUNT="/data"

if lsblk | grep -q "xvdf"; then
  if ! blkid "$DATA_DEVICE" | grep -q "ext4"; then
    log "Formatting $DATA_DEVICE as ext4..."
    mkfs.ext4 -L chronopoli-data "$DATA_DEVICE"
  fi

  mkdir -p "$DATA_MOUNT"

  if ! mount | grep -q "$DATA_MOUNT"; then
    mount "$DATA_DEVICE" "$DATA_MOUNT"
  fi

  # Persist in fstab
  if ! grep -q "$DATA_MOUNT" /etc/fstab; then
    echo "LABEL=chronopoli-data $DATA_MOUNT ext4 defaults,nofail 0 2" >> /etc/fstab
  fi

  # Create directory structure
  mkdir -p "$DATA_MOUNT"/{tutor,backups,logs}
  chown -R ubuntu:ubuntu "$DATA_MOUNT"
  log "Data volume mounted at $DATA_MOUNT ✓"
else
  warn "No EBS data volume found at $DATA_DEVICE — skipping mount"
  warn "Tutor will use default paths"
fi

# ============================================================
# 4. SWAP (4GB for t3.xlarge with 16GB RAM)
# ============================================================
log "Step 4/8: Configuring swap..."
if ! swapon --show | grep -q "/swapfile"; then
  fallocate -l 4G /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile

  if ! grep -q "/swapfile" /etc/fstab; then
    echo "/swapfile none swap sw 0 0" >> /etc/fstab
  fi
fi

# Tune swappiness for production
sysctl vm.swappiness=10
echo "vm.swappiness=10" > /etc/sysctl.d/99-chronopoli.conf

log "Swap configured (4GB) ✓"

# ============================================================
# 5. FIREWALL (UFW)
# ============================================================
log "Step 5/8: Configuring firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    comment "SSH"
ufw allow 80/tcp    comment "HTTP"
ufw allow 443/tcp   comment "HTTPS"
ufw --force enable

log "Firewall active: SSH(22), HTTP(80), HTTPS(443) ✓"

# ============================================================
# 6. FAIL2BAN (SSH brute-force protection)
# ============================================================
log "Step 6/8: Configuring fail2ban..."
cat > /etc/fail2ban/jail.local <<'JAIL'
[DEFAULT]
bantime  = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port    = ssh
filter  = sshd
logpath = /var/log/auth.log
JAIL

systemctl enable fail2ban
systemctl restart fail2ban
log "Fail2ban configured ✓"

# ============================================================
# 7. TUTOR
# ============================================================
log "Step 7/8: Installing Tutor..."

# Use /data/tutor if data volume is mounted, otherwise default
if [[ -d "/data/tutor" ]]; then
  export TUTOR_ROOT="/data/tutor"
  echo "export TUTOR_ROOT=/data/tutor" >> /home/ubuntu/.bashrc
  log "Tutor root set to /data/tutor (EBS volume)"
fi

# Install Tutor in a virtualenv for isolation
VENV_DIR="/opt/chronopoli/venv"
mkdir -p /opt/chronopoli
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

pip install --upgrade pip
pip install "tutor[full]"

# Create symlink so tutor is on PATH
ln -sf "$VENV_DIR/bin/tutor" /usr/local/bin/tutor

deactivate

log "Tutor installed: $(tutor --version) ✓"

# ============================================================
# 8. SYSTEM LIMITS (for Docker/OpenEdX)
# ============================================================
log "Step 8/8: Tuning system limits..."

cat > /etc/security/limits.d/99-chronopoli.conf <<'LIMITS'
# Chronopoli – OpenEdX requires higher file descriptor limits
*       soft    nofile    65535
*       hard    nofile    65535
ubuntu  soft    nofile    65535
ubuntu  hard    nofile    65535
LIMITS

# Kernel parameters for production workloads
cat >> /etc/sysctl.d/99-chronopoli.conf <<'SYSCTL'
# Network tuning
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.ip_local_port_range = 1024 65535
# File watches for OpenEdX
fs.inotify.max_user_watches = 524288
SYSCTL

sysctl -p /etc/sysctl.d/99-chronopoli.conf

log "System limits configured ✓"

# ============================================================
# SUMMARY
# ============================================================
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  CHRONOPOLI SERVER SETUP COMPLETE ✓                      ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║                                                          ║"
echo "║  Installed:                                              ║"
echo "║    • Docker $(docker --version 2>/dev/null | awk '{print $3}' | tr -d ',')                                   ║"
echo "║    • Tutor $(tutor --version 2>/dev/null | awk '{print $NF}')                                    ║"
echo "║    • UFW firewall (22, 80, 443)                          ║"
echo "║    • Fail2ban (SSH protection)                           ║"
echo "║    • 4GB swap                                            ║"
echo "║                                                          ║"
if [[ -d "/data/tutor" ]]; then
echo "║  Data volume: /data (EBS)                                ║"
echo "║  Tutor root:  /data/tutor                                ║"
else
echo "║  Data volume: Not mounted (using defaults)               ║"
fi
echo "║                                                          ║"
echo "║  NEXT STEP:                                              ║"
echo "║  Run: bash configure-tutor.sh                            ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
