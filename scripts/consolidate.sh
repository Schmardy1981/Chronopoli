#!/bin/bash
# ============================================================
# CHRONOPOLI – Consolidation Script
# Pulls OpenEdX upstream refs + all Chronopoli assets into
# one analysable folder structure for Claude Code
#
# Run this ONCE on your local machine before starting Claude Code
# Usage: ./scripts/consolidate.sh
# ============================================================

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UPSTREAM_DIR="${ROOT_DIR}/.upstream"
DOCS_SOURCE="${ROOT_DIR}/docs/source"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[GSD]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# ============================================================
# STEP 1 – Create folder structure
# ============================================================
log "Creating consolidated workspace..."

mkdir -p "${UPSTREAM_DIR}"
mkdir -p "${DOCS_SOURCE}"
mkdir -p "${ROOT_DIR}/.planning"
mkdir -p "${ROOT_DIR}/infrastructure/terraform"
mkdir -p "${ROOT_DIR}/infrastructure/kubernetes/helm"

# ============================================================
# STEP 2 – Clone/update OpenEdX upstream references
# (shallow clones – we don't fork, just reference)
# ============================================================
log "Pulling OpenEdX upstream references (shallow)..."

clone_or_update() {
  local repo=$1
  local dir=$2
  local name=$3
  
  if [[ -d "${UPSTREAM_DIR}/${dir}/.git" ]]; then
    log "Updating ${name}..."
    git -C "${UPSTREAM_DIR}/${dir}" pull --quiet
  else
    log "Cloning ${name} (shallow)..."
    git clone --depth=1 --quiet "https://github.com/${repo}.git" \
      "${UPSTREAM_DIR}/${dir}"
  fi
}

# Core platform (we need this for reference, not to run directly)
clone_or_update "openedx/openedx-platform" "openedx-platform" "OpenEdX Platform"

# Tutor – our deployment engine
clone_or_update "overhangio/tutor" "tutor-core" "Tutor"

# Key Tutor plugins we'll reference
clone_or_update "overhangio/tutor-mfe" "tutor-mfe" "Tutor MFE Plugin"

# Frontend app authoring (Studio MFE) – for theme reference
clone_or_update "openedx/frontend-app-authoring" "frontend-app-authoring" "Studio MFE"

log "OpenEdX references ready ✓"

# ============================================================
# STEP 3 – Copy PDFs/strategy docs into docs/source
# ============================================================
log "Consolidating strategy documents..."

# Copy PDFs if they exist in common locations
for pdf_dir in ~/Downloads ~/Desktop ~/Documents "$HOME"; do
  for pdf in chronopoli_strategy_detailed.pdf \
              chronopoli_digital_campus_architecture.pdf; do
    if [[ -f "${pdf_dir}/${pdf}" ]]; then
      cp "${pdf_dir}/${pdf}" "${DOCS_SOURCE}/"
      log "Copied ${pdf} ✓"
    fi
  done
done

# ============================================================
# STEP 4 – Generate GSD initial config
# ============================================================
log "Setting up GSD configuration..."

cat > "${ROOT_DIR}/.planning/config.json" << 'EOF'
{
  "project": "Chronopoli",
  "version": "1.0.0",
  "granularity": "standard",
  "models": {
    "research": "claude-sonnet-4-6",
    "planning": "claude-opus-4-6",
    "execution": "claude-sonnet-4-6",
    "completion": "claude-sonnet-4-6"
  },
  "git": {
    "default_branch": "main",
    "develop_branch": "develop",
    "commit_format": "conventional"
  },
  "hooks": {
    "context_monitor": true,
    "auto_advance": true,
    "verify_work": true
  },
  "workflow": {
    "discuss": true,
    "research": true,
    "plan_check": true,
    "post_verify": true
  }
}
EOF

log "GSD config created ✓"

# ============================================================
# STEP 5 – Generate ROADMAP.md for GSD
# ============================================================
cat > "${ROOT_DIR}/.planning/ROADMAP.md" << 'EOF'
# CHRONOPOLI – GSD ROADMAP

## Milestone 1: Foundation (AWS + OpenEdX Running)
**Goal:** Platform accessible at learn.chronopoli.io

### Phases
- [ ] P1: Terraform – provision EC2, RDS, S3, CloudFront, Route53
- [ ] P2: OpenEdX – Tutor install, configure, SSL
- [ ] P3: Theme – deploy chronopoli-theme, verify visually
- [ ] P4: Districts – create 6 organizations in OpenEdX
- [ ] P5: Admin – create admin users, smoke test

---

## Milestone 2: AI Onboarding + Districts
**Goal:** New users get personalized district recommendations

### Phases
- [ ] P1: Django app – chronopoli_onboarding models + views
- [ ] P2: Templates – onboarding questionnaire UI (dark theme)
- [ ] P3: Signal hooks – redirect after registration
- [ ] P4: Results page – district + course recommendations
- [ ] P5: Testing – full user journey smoke test

---

## Milestone 3: Partner Ecosystem
**Goal:** First partner track live (Ripple or Cardano)

### Phases
- [ ] P1: Partner Django app – models, admin interface
- [ ] P2: OpenEdX org setup – partner organization + course
- [ ] P3: Partner portal – content upload workflow
- [ ] P4: Co-branded course page – partner branding in theme
- [ ] P5: Certificate – Accredible integration

---

## Milestone 4: Auto-Scaling (Kubernetes)
**Goal:** Platform auto-scales on AWS EKS

### Phases
- [ ] P1: EKS cluster – Terraform for Kubernetes cluster
- [ ] P2: Tutor k8s – migrate from Docker to Kubernetes mode
- [ ] P3: HPA config – Horizontal Pod Autoscaler for LMS/CMS/workers
- [ ] P4: Helm chart – package Chronopoli deployment
- [ ] P5: Load test – verify scaling under simulated traffic
EOF

log "Roadmap created ✓"

# ============================================================
# STEP 6 – Install GSD into project
# ============================================================
log "Installing GSD framework locally..."

if command -v npx &> /dev/null; then
  cd "${ROOT_DIR}"
  npx get-shit-done-cc --claude --local
  log "GSD installed ✓"
else
  warn "npx not found. Install Node.js then run:"
  warn "  npx get-shit-done-cc --claude --local"
fi

# ============================================================
# STEP 7 – Generate the Claude Code master prompt
# ============================================================
log "Generating Claude Code kickoff prompt..."

cat > "${ROOT_DIR}/KICKOFF_PROMPT.md" << 'KICKOFF'
# CHRONOPOLI – Claude Code Kickoff Prompt
# Copy-paste this into Claude Code to start a session

---

I am working on Chronopoli – a global knowledge platform built on OpenEdX,
deployed on AWS, using the GSD framework for structured development.

**First action:** Read `CLAUDE.md` in the project root completely.
Then read `.planning/ROADMAP.md` to understand the current milestone.
Then check `.planning/` for any active GSD state.

**Project context summary:**
- OpenEdX LMS + Studio via Tutor (Docker → Kubernetes)
- 6 Knowledge Districts (AI, Digital Assets, Governance, Compliance, Investigation, Risk & Trust)
- AWS: EC2 Phase 1 → EKS auto-scaling Phase 2
- Custom theme: dark/gold Dubai aesthetic
- AI onboarding: 5-question district router (replaces Engagely AI)
- Partners: Ripple, Cardano, Chainalysis, TRM Labs, Microsoft AI etc.

**Upstream references available in `.upstream/`:**
- `.upstream/openedx-platform/` – OpenEdX source (read-only reference)
- `.upstream/tutor-core/` – Tutor deployment engine
- `.upstream/frontend-app-authoring/` – Studio MFE

**We do NOT fork openedx-platform.**
We extend via Tutor plugins in `tutor/plugins/` and `plugins/`.

**Current working milestone:** Check `.planning/ROADMAP.md`

Now run: `/gsd:new-project` or `/gsd:new-milestone` based on current state.

---
KICKOFF

log "Kickoff prompt created at KICKOFF_PROMPT.md ✓"

# ============================================================
# FINAL SUMMARY
# ============================================================
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  CHRONOPOLI CONSOLIDATION COMPLETE                          ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║                                                              ║"
echo "║  Repository ready for Claude Code + GSD                     ║"
echo "║                                                              ║"
echo "║  NEXT STEPS:                                                 ║"
echo "║                                                              ║"
echo "║  1. Open Claude Code in this directory:                      ║"
echo "║     claude                                                   ║"
echo "║                                                              ║"
echo "║  2. Copy KICKOFF_PROMPT.md into Claude Code                  ║"
echo "║                                                              ║"
echo "║  3. Then run:                                                ║"
echo "║     /gsd:new-project                                         ║"
echo "║                                                              ║"
echo "║  4. GSD will guide you through:                              ║"
echo "║     discuss → plan → build → verify → commit                 ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "  Structure:"
find "${ROOT_DIR}" -not -path '*/.git/*' \
                   -not -path '*/.upstream/*' \
                   -not -path '*/node_modules/*' \
                   -not -path '*/__pycache__/*' \
                   -maxdepth 3 -type f | sort
echo ""
