#!/bin/bash
# ============================================================
# Chronopoli – Health Check & Smoke Test Script
# Verifies that the platform is running correctly.
# Usage: bash healthcheck.sh [--domain learn.chronopoli.io]
# ============================================================

set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASS=0
FAIL=0
WARN=0

check_pass() { echo -e "  ${GREEN}✓ PASS${NC} $1"; PASS=$((PASS + 1)); }
check_fail() { echo -e "  ${RED}✗ FAIL${NC} $1"; FAIL=$((FAIL + 1)); }
check_warn() { echo -e "  ${YELLOW}⚠ WARN${NC} $1"; WARN=$((WARN + 1)); }
info() { echo -e "  ${BLUE}ℹ INFO${NC} $1"; }

# ============================================================
# DETERMINE DOMAIN
# ============================================================
if [[ "${1:-}" == "--domain" ]] && [[ -n "${2:-}" ]]; then
  LMS_HOST="$2"
else
  LMS_HOST=$(tutor config printvalue LMS_HOST 2>/dev/null || echo "learn.chronopoli.io")
fi
CMS_HOST=$(tutor config printvalue CMS_HOST 2>/dev/null || echo "studio.chronopoli.io")

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  CHRONOPOLI HEALTH CHECK                                 ║"
echo "║  LMS: https://${LMS_HOST}                               "
echo "║  CMS: https://${CMS_HOST}                               "
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# ============================================================
# 1. DOCKER CONTAINERS
# ============================================================
echo -e "${BLUE}[1/8] Docker Containers${NC}"

EXPECTED_CONTAINERS=("lms" "cms" "lms-worker" "cms-worker" "caddy" "mongodb" "elasticsearch")

for container in "${EXPECTED_CONTAINERS[@]}"; do
  if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "$container"; then
    check_pass "$container running"
  else
    check_fail "$container not running"
  fi
done

# Check Redis (may be external)
if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "redis"; then
  check_pass "redis running (Docker)"
elif [[ -n "${REDIS_HOST:-}" ]]; then
  check_pass "redis external (ElastiCache)"
else
  check_warn "redis status unknown"
fi

# Check MySQL (should be external for production)
if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "mysql"; then
  check_warn "mysql running in Docker (should be RDS for production)"
else
  check_pass "mysql external (RDS)"
fi

echo ""

# ============================================================
# 2. LMS HEALTH
# ============================================================
echo -e "${BLUE}[2/8] LMS Health${NC}"

# Heartbeat endpoint
HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" "https://${LMS_HOST}/heartbeat" 2>/dev/null || echo "000")
if [[ "$HTTP_CODE" == "200" ]]; then
  check_pass "LMS heartbeat (200)"
else
  check_fail "LMS heartbeat returned $HTTP_CODE"
fi

# Homepage
HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" "https://${LMS_HOST}/" 2>/dev/null || echo "000")
if [[ "$HTTP_CODE" == "200" ]]; then
  check_pass "LMS homepage (200)"
else
  check_fail "LMS homepage returned $HTTP_CODE"
fi

# Login page
HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" "https://${LMS_HOST}/login" 2>/dev/null || echo "000")
if [[ "$HTTP_CODE" == "200" ]]; then
  check_pass "LMS login page (200)"
else
  check_fail "LMS login page returned $HTTP_CODE"
fi

# Registration page
HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" "https://${LMS_HOST}/register" 2>/dev/null || echo "000")
if [[ "$HTTP_CODE" == "200" ]]; then
  check_pass "LMS registration page (200)"
else
  check_fail "LMS registration page returned $HTTP_CODE"
fi

echo ""

# ============================================================
# 3. CMS (STUDIO) HEALTH
# ============================================================
echo -e "${BLUE}[3/8] Studio (CMS) Health${NC}"

HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" "https://${CMS_HOST}/heartbeat" 2>/dev/null || echo "000")
if [[ "$HTTP_CODE" == "200" ]]; then
  check_pass "Studio heartbeat (200)"
else
  check_fail "Studio heartbeat returned $HTTP_CODE"
fi

HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" "https://${CMS_HOST}/signin" 2>/dev/null || echo "000")
if [[ "$HTTP_CODE" =~ ^(200|302)$ ]]; then
  check_pass "Studio signin page ($HTTP_CODE)"
else
  check_fail "Studio signin returned $HTTP_CODE"
fi

echo ""

# ============================================================
# 4. API ENDPOINTS
# ============================================================
echo -e "${BLUE}[4/8] API Endpoints${NC}"

# Course API
HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" "https://${LMS_HOST}/api/courses/v1/courses/" 2>/dev/null || echo "000")
if [[ "$HTTP_CODE" =~ ^(200|401|403)$ ]]; then
  check_pass "Course API responding ($HTTP_CODE)"
else
  check_fail "Course API returned $HTTP_CODE"
fi

# User API
HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" "https://${LMS_HOST}/api/user/v1/me" 2>/dev/null || echo "000")
if [[ "$HTTP_CODE" =~ ^(200|401|403)$ ]]; then
  check_pass "User API responding ($HTTP_CODE)"
else
  check_fail "User API returned $HTTP_CODE"
fi

# Enrollment API
HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" "https://${LMS_HOST}/api/enrollment/v1/enrollment" 2>/dev/null || echo "000")
if [[ "$HTTP_CODE" =~ ^(200|401|403)$ ]]; then
  check_pass "Enrollment API responding ($HTTP_CODE)"
else
  check_fail "Enrollment API returned $HTTP_CODE"
fi

echo ""

# ============================================================
# 5. SSL CERTIFICATE
# ============================================================
echo -e "${BLUE}[5/8] SSL Certificate${NC}"

SSL_EXPIRY=$(echo | openssl s_client -servername "$LMS_HOST" -connect "${LMS_HOST}:443" 2>/dev/null | \
  openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)

if [[ -n "$SSL_EXPIRY" ]]; then
  EXPIRY_EPOCH=$(date -d "$SSL_EXPIRY" +%s 2>/dev/null || date -j -f "%b %d %H:%M:%S %Y %Z" "$SSL_EXPIRY" +%s 2>/dev/null || echo "0")
  NOW_EPOCH=$(date +%s)
  DAYS_LEFT=$(( (EXPIRY_EPOCH - NOW_EPOCH) / 86400 ))

  if [[ $DAYS_LEFT -gt 30 ]]; then
    check_pass "SSL valid, expires in ${DAYS_LEFT} days ($SSL_EXPIRY)"
  elif [[ $DAYS_LEFT -gt 0 ]]; then
    check_warn "SSL expires in ${DAYS_LEFT} days — renew soon!"
  else
    check_fail "SSL certificate expired!"
  fi
else
  check_warn "Could not verify SSL certificate"
fi

echo ""

# ============================================================
# 6. KNOWLEDGE DISTRICTS (Organizations)
# ============================================================
echo -e "${BLUE}[6/8] Knowledge Districts${NC}"

DISTRICT_OUTPUT=$(tutor local exec lms python manage.py shell -c "
from organizations.models import Organization
districts = ['CHRON-AI','CHRON-DA','CHRON-GOV','CHRON-COMP','CHRON-INV','CHRON-RISK']
for code in districts:
    exists = Organization.objects.filter(short_name=code).exists()
    print(f'{code}:{exists}')
" 2>/dev/null || echo "")

if [[ -n "$DISTRICT_OUTPUT" ]]; then
  while IFS= read -r line; do
    CODE=$(echo "$line" | cut -d: -f1)
    EXISTS=$(echo "$line" | cut -d: -f2)
    if [[ "$EXISTS" == "True" ]]; then
      check_pass "District $CODE exists"
    else
      check_fail "District $CODE missing"
    fi
  done <<< "$DISTRICT_OUTPUT"
else
  check_warn "Could not verify districts (LMS may not be accessible)"
fi

echo ""

# ============================================================
# 7. DATABASE CONNECTIVITY
# ============================================================
echo -e "${BLUE}[7/8] Database${NC}"

DB_CHECK=$(tutor local exec lms python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT 1')
print('OK')
" 2>/dev/null || echo "FAIL")

if echo "$DB_CHECK" | grep -q "OK"; then
  check_pass "MySQL database connection"
else
  check_fail "MySQL database connection failed"
fi

echo ""

# ============================================================
# 8. DISK & MEMORY
# ============================================================
echo -e "${BLUE}[8/8] System Resources${NC}"

# Disk usage
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | tr -d '%')
if [[ $DISK_USAGE -lt 80 ]]; then
  check_pass "Disk usage: ${DISK_USAGE}%"
elif [[ $DISK_USAGE -lt 90 ]]; then
  check_warn "Disk usage: ${DISK_USAGE}% — consider cleanup"
else
  check_fail "Disk usage: ${DISK_USAGE}% — critical!"
fi

# Memory
MEM_AVAILABLE=$(free -m | awk '/^Mem:/ {printf "%.0f", $7/$2*100}')
if [[ $MEM_AVAILABLE -gt 20 ]]; then
  check_pass "Memory available: ${MEM_AVAILABLE}%"
elif [[ $MEM_AVAILABLE -gt 10 ]]; then
  check_warn "Memory available: ${MEM_AVAILABLE}% — low"
else
  check_fail "Memory available: ${MEM_AVAILABLE}% — critical!"
fi

# Docker disk
DOCKER_DISK=$(docker system df --format '{{.Size}}' 2>/dev/null | head -1 || echo "unknown")
info "  Docker disk usage: $DOCKER_DISK"

echo ""

# ============================================================
# RESULT SUMMARY
# ============================================================
TOTAL=$((PASS + FAIL + WARN))
echo "╔══════════════════════════════════════════════════════════╗"
if [[ $FAIL -eq 0 ]]; then
  echo -e "║  ${GREEN}RESULT: ALL CHECKS PASSED${NC}                               ║"
else
  echo -e "║  ${RED}RESULT: ${FAIL} CHECK(S) FAILED${NC}                              ║"
fi
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  Passed:   $PASS / $TOTAL                                        "
echo "║  Failed:   $FAIL / $TOTAL                                        "
echo "║  Warnings: $WARN / $TOTAL                                        "
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

exit $FAIL
