#!/bin/bash
# ============================================================
# Chronopoli – Discourse Category & Group Setup
# Creates district categories, sub-categories, and groups.
# Run AFTER Discourse is installed and API key is generated.
# Usage: bash setup-discourse-categories.sh [--env-file /path/to/.env]
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'
log()  { echo -e "${GREEN}[DISCOURSE]${NC} $1"; }
err()  { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Load env
for candidate in "${2:-}" "$REPO_DIR/infrastructure/extensions/.env" "/data/chronopoli/extensions.env"; do
  if [[ -n "$candidate" ]] && [[ -f "$candidate" ]]; then
    set -a; source "$candidate"; set +a
    break
  fi
done

DISCOURSE_URL="https://${DISCOURSE_HOSTNAME:-community.chronopoli.io}"
API_KEY="${DISCOURSE_API_KEY:-}"
API_USER="admin"

if [[ -z "$API_KEY" ]]; then
  err "DISCOURSE_API_KEY not set. Generate one in Discourse Admin → API"
fi

# ============================================================
# HELPER: Create category, return ID
# ============================================================
create_category() {
  local name="$1"
  local color="$2"
  local parent_id="${3:-}"

  local data="name=$name&color=$color&text_color=FFFFFF"
  if [[ -n "$parent_id" ]]; then
    data="$data&parent_category_id=$parent_id"
  fi

  local response
  response=$(curl -s -X POST "$DISCOURSE_URL/categories.json" \
    -H "Api-Key: $API_KEY" \
    -H "Api-Username: $API_USER" \
    -d "$data")

  local cat_id
  cat_id=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('category',{}).get('id',''))" 2>/dev/null || echo "")

  if [[ -n "$cat_id" ]]; then
    log "  Created: $name (ID: $cat_id)"
    echo "$cat_id"
  else
    log "  Exists or error: $name"
    # Try to find existing
    cat_id=$(curl -s "$DISCOURSE_URL/categories.json" \
      -H "Api-Key: $API_KEY" -H "Api-Username: $API_USER" | \
      python3 -c "
import sys, json
data = json.load(sys.stdin)
for c in data.get('category_list',{}).get('categories',[]):
    if c['name'] == '$name':
        print(c['id'])
        break
" 2>/dev/null || echo "")
    echo "$cat_id"
  fi
}

# ============================================================
# HELPER: Create group
# ============================================================
create_group() {
  local name="$1"
  local full_name="$2"

  curl -s -X POST "$DISCOURSE_URL/admin/groups.json" \
    -H "Api-Key: $API_KEY" \
    -H "Api-Username: $API_USER" \
    -H "Content-Type: application/json" \
    -d "{\"group\":{\"name\":\"$name\",\"full_name\":\"$full_name\",\"visibility_level\":0,\"members_visibility_level\":0}}" > /dev/null 2>&1

  log "  Group: $name ($full_name)"
}

# ============================================================
# 1. CREATE DISTRICT GROUPS
# ============================================================
log "Creating district groups..."

create_group "ai-district"              "AI District Members"
create_group "digital-assets-district"  "Digital Assets District Members"
create_group "governance-district"      "Governance District Members"
create_group "compliance-district"      "Compliance District Members"
create_group "investigation-district"   "Investigation District Members"
create_group "risk-trust-district"      "Risk & Trust District Members"

log "Groups created ✓"

# ============================================================
# 2. CREATE TOP-LEVEL DISTRICT CATEGORIES
# ============================================================
log "Creating district categories..."

AI_ID=$(create_category "AI District" "6C63FF")
DA_ID=$(create_category "Digital Assets District" "F59E0B")
GOV_ID=$(create_category "Governance District" "10B981")
COMP_ID=$(create_category "Compliance District" "3B82F6")
INV_ID=$(create_category "Investigation District" "EF4444")
RISK_ID=$(create_category "Risk and Trust District" "8B5CF6")

log "District categories created ✓"

# ============================================================
# 3. CREATE SUB-CATEGORIES (Learning Layers + Partner Tracks)
# ============================================================
log "Creating sub-categories..."

# AI District
if [[ -n "$AI_ID" ]]; then
  create_category "Entry Level"     "6C63FF" "$AI_ID"
  create_category "Professional"    "6C63FF" "$AI_ID"
  create_category "Institutional"   "6C63FF" "$AI_ID"
  create_category "Partner Tracks"  "6C63FF" "$AI_ID"
fi

# Digital Assets District
if [[ -n "$DA_ID" ]]; then
  create_category "Entry Level"     "F59E0B" "$DA_ID"
  create_category "Professional"    "F59E0B" "$DA_ID"
  create_category "Institutional"   "F59E0B" "$DA_ID"
  create_category "Partner Tracks"  "F59E0B" "$DA_ID"
  create_category "Ripple Track"    "F59E0B" "$DA_ID"
  create_category "Cardano Track"   "F59E0B" "$DA_ID"
fi

# Governance District
if [[ -n "$GOV_ID" ]]; then
  create_category "Entry Level"     "10B981" "$GOV_ID"
  create_category "Professional"    "10B981" "$GOV_ID"
  create_category "Institutional"   "10B981" "$GOV_ID"
  create_category "Partner Tracks"  "10B981" "$GOV_ID"
fi

# Compliance District
if [[ -n "$COMP_ID" ]]; then
  create_category "Entry Level"     "3B82F6" "$COMP_ID"
  create_category "Professional"    "3B82F6" "$COMP_ID"
  create_category "Institutional"   "3B82F6" "$COMP_ID"
  create_category "Partner Tracks"  "3B82F6" "$COMP_ID"
fi

# Investigation District
if [[ -n "$INV_ID" ]]; then
  create_category "Entry Level"     "EF4444" "$INV_ID"
  create_category "Professional"    "EF4444" "$INV_ID"
  create_category "Institutional"   "EF4444" "$INV_ID"
  create_category "Partner Tracks"  "EF4444" "$INV_ID"
  create_category "Chainalysis Track" "EF4444" "$INV_ID"
  create_category "TRM Labs Track"  "EF4444" "$INV_ID"
fi

# Risk & Trust District
if [[ -n "$RISK_ID" ]]; then
  create_category "Entry Level"     "8B5CF6" "$RISK_ID"
  create_category "Professional"    "8B5CF6" "$RISK_ID"
  create_category "Institutional"   "8B5CF6" "$RISK_ID"
  create_category "Partner Tracks"  "8B5CF6" "$RISK_ID"
fi

log "Sub-categories created ✓"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  DISCOURSE CATEGORIES COMPLETE ✓                         ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  6 district groups created                               ║"
echo "║  6 top-level categories                                  ║"
echo "║  24+ sub-categories (layers + partner tracks)            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
