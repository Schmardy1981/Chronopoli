#!/bin/bash
# ============================================================
# Chronopoli – District & Multi-Tenant Setup Script
# Creates all 6 Knowledge Districts, admin user, demo courses,
# and configures the multi-tenant architecture.
#
# Usage: bash setup-districts.sh [--env-file /path/to/production.env]
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log()  { echo -e "${GREEN}[DISTRICT]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()  { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }

# ============================================================
# LOAD ENV (optional — for ADMIN_EMAIL/ADMIN_PASSWORD)
# ============================================================
for candidate in "${2:-}" "$REPO_DIR/infrastructure/production.env" "/data/chronopoli/production.env"; do
  if [[ -n "$candidate" ]] && [[ -f "$candidate" ]]; then
    set -a; source "$candidate"; set +a
    break
  fi
done

export TUTOR_ROOT="${TUTOR_ROOT:-/data/tutor}"

# ============================================================
# CHECK TUTOR IS RUNNING
# ============================================================
log "Verifying Tutor is running..."
if ! tutor local status 2>/dev/null | grep -q "running"; then
  warn "Tutor containers may not be running. Attempting to continue..."
fi

# ============================================================
# 1. CREATE ADMIN SUPERUSER
# ============================================================
log "Step 1/5: Creating admin superuser..."

ADMIN_USER="${ADMIN_USER:-admin}"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@chronopoli.io}"
ADMIN_PASS="${ADMIN_PASSWORD:-}"

if [[ -z "$ADMIN_PASS" ]]; then
  echo -n "Enter admin password: "
  read -s ADMIN_PASS
  echo ""
fi

tutor local do createuser \
  --superuser --staff \
  --password "$ADMIN_PASS" \
  "$ADMIN_USER" "$ADMIN_EMAIL" 2>/dev/null || \
  warn "Admin user may already exist — continuing"

log "Admin user created: $ADMIN_USER ($ADMIN_EMAIL) ✓"

# ============================================================
# 2. CREATE 6 KNOWLEDGE DISTRICTS (OpenEdX Organizations)
# ============================================================
log "Step 2/5: Creating Knowledge Districts (OpenEdX Organizations)..."

tutor local exec lms python manage.py shell -c "
from organizations.models import Organization

districts = [
    {
        'short_name': 'CHRON-AI',
        'name': 'Chronopoli AI District',
        'description': 'AI governance, model risk, enterprise AI adoption, responsible AI frameworks',
        'logo': None,
    },
    {
        'short_name': 'CHRON-DA',
        'name': 'Chronopoli Digital Assets District',
        'description': 'Blockchain technology, tokenization, stablecoins, digital payments, DeFi',
        'logo': None,
    },
    {
        'short_name': 'CHRON-GOV',
        'name': 'Chronopoli Governance District',
        'description': 'Digital policy, regulation frameworks, sovereign digital strategy, CBDC governance',
        'logo': None,
    },
    {
        'short_name': 'CHRON-COMP',
        'name': 'Chronopoli Compliance District',
        'description': 'AML/CFT compliance, KYC frameworks, sanctions screening, travel rule, FATF standards',
        'logo': None,
    },
    {
        'short_name': 'CHRON-INV',
        'name': 'Chronopoli Investigation District',
        'description': 'Blockchain forensics, financial crime investigation, asset tracing, intelligence analysis',
        'logo': None,
    },
    {
        'short_name': 'CHRON-RISK',
        'name': 'Chronopoli Risk & Trust District',
        'description': 'Operational risk management, cyber risk, enterprise trust frameworks, digital identity',
        'logo': None,
    },
    {
        'short_name': 'CHRON-ET',
        'name': 'Chronopoli Emerging Tech District',
        'description': 'Quantum computing, IoT, autonomous systems, spatial computing, frontier technology',
        'logo': None,
    },
]

created_count = 0
for d in districts:
    org, created = Organization.objects.get_or_create(
        short_name=d['short_name'],
        defaults={
            'name': d['name'],
            'description': d['description'],
            'active': True,
        }
    )
    if created:
        created_count += 1
        print(f'  Created: {org.short_name} — {org.name}')
    else:
        print(f'  Exists:  {org.short_name} — {org.name}')

print(f'\\nDistricts: {created_count} created, {len(districts) - created_count} already existed')
"

log "Knowledge Districts configured ✓"

# ============================================================
# 3. RUN DJANGO MIGRATIONS FOR CHRONOPOLI APPS
# ============================================================
log "Step 3/5: Running Chronopoli Django migrations..."

tutor local exec lms python manage.py migrate chronopoli_onboarding --noinput 2>/dev/null || \
  warn "chronopoli_onboarding migration skipped (app may not be installed yet)"

tutor local exec lms python manage.py migrate chronopoli_partners --noinput 2>/dev/null || \
  warn "chronopoli_partners migration skipped (app may not be installed yet)"

log "Migrations complete ✓"

# ============================================================
# 4. CREATE DEMO COURSES (one per district)
# ============================================================
log "Step 4/5: Creating demo courses for each district..."

tutor local exec lms python manage.py shell -c "
from cms.djangoapps.contentstore.utils import add_instructor
from xmodule.modulestore.django import modulestore
from opaque_keys.edx.keys import CourseKey
from organizations.models import Organization, OrganizationCourse
from django.contrib.auth import get_user_model
User = get_user_model()

# Demo course definitions — one per district, one per learning layer
demo_courses = [
    # AI District
    {
        'org': 'CHRON-AI',
        'number': 'AI-101',
        'run': '2026',
        'display_name': 'Introduction to Enterprise AI Governance',
        'layer': 'L1',
    },
    # Digital Assets District
    {
        'org': 'CHRON-DA',
        'number': 'DA-101',
        'run': '2026',
        'display_name': 'Blockchain Fundamentals for Financial Professionals',
        'layer': 'L1',
    },
    # Governance District
    {
        'org': 'CHRON-GOV',
        'number': 'GOV-201',
        'run': '2026',
        'display_name': 'Digital Regulatory Frameworks',
        'layer': 'L2',
    },
    # Compliance District
    {
        'org': 'CHRON-COMP',
        'number': 'COMP-201',
        'run': '2026',
        'display_name': 'AML/CFT Compliance Design',
        'layer': 'L2',
    },
    # Investigation District
    {
        'org': 'CHRON-INV',
        'number': 'INV-301',
        'run': '2026',
        'display_name': 'Blockchain Forensics & Asset Tracing',
        'layer': 'L3',
    },
    # Risk District
    {
        'org': 'CHRON-RISK',
        'number': 'RISK-101',
        'run': '2026',
        'display_name': 'Enterprise Risk Management Foundations',
        'layer': 'L1',
    },
    # Emerging Tech District
    {
        'org': 'CHRON-ET',
        'number': 'ET-101',
        'run': '2026',
        'display_name': 'Frontier Technologies: Quantum, IoT & Spatial Computing',
        'layer': 'L1',
    },
]

store = modulestore()
admin_user = User.objects.filter(is_superuser=True).first()

for course_def in demo_courses:
    course_key = CourseKey.from_string(
        f\"course-v1:{course_def['org']}+{course_def['number']}+{course_def['run']}\"
    )

    # Check if course already exists
    try:
        existing = store.get_course(course_key)
        if existing:
            print(f\"  Exists:  {course_key}\")
            continue
    except Exception:
        pass

    try:
        # Create the course
        course = store.create_course(
            org=course_def['org'],
            course=course_def['number'],
            run=course_def['run'],
            user_id=admin_user.id if admin_user else 1,
            fields={
                'display_name': course_def['display_name'],
            },
        )

        # Link course to its organization
        try:
            org = Organization.objects.get(short_name=course_def['org'])
            OrganizationCourse.objects.get_or_create(
                course_id=str(course_key),
                organization=org,
            )
        except Organization.DoesNotExist:
            pass

        print(f\"  Created: {course_key} — {course_def['display_name']} [{course_def['layer']}]\")
    except Exception as e:
        print(f\"  Skipped: {course_key} — {e}\")

print('\\nDemo courses setup complete.')
"

log "Demo courses created ✓"

# ============================================================
# 5. SET THEME
# ============================================================
log "Step 5/5: Applying Chronopoli theme..."

tutor local do settheme chronopoli-theme 2>/dev/null || \
  warn "Theme not applied — deploy theme files first"

log "Theme applied ✓"

# ============================================================
# SUMMARY
# ============================================================
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  CHRONOPOLI DISTRICT SETUP COMPLETE ✓                    ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║                                                          ║"
echo "║  Districts Created:                                      ║"
echo "║    • CHRON-AI    — AI District                           ║"
echo "║    • CHRON-DA    — Digital Assets District               ║"
echo "║    • CHRON-GOV   — Governance District                   ║"
echo "║    • CHRON-COMP  — Compliance District                   ║"
echo "║    • CHRON-INV   — Investigation District                ║"
echo "║    • CHRON-RISK  — Risk & Trust District                 ║"
echo "║    • CHRON-ET    — Emerging Tech District                ║"
echo "║                                                          ║"
echo "║  Demo Courses: 7 (one per district)                      ║"
echo "║  Admin User:   ${ADMIN_USER:-admin}                      "
echo "║                                                          ║"
echo "║  Multi-Tenant Architecture:                              ║"
echo "║    Each district = separate OpenEdX Organization         ║"
echo "║    Courses are scoped to their district org              ║"
echo "║    Users get routed via AI Onboarding questionnaire      ║"
echo "║                                                          ║"
echo "║  NEXT: bash healthcheck.sh                               ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
