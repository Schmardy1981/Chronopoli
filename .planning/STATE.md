# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-17)

**Core value:** Professionals in regulated industries can discover the right knowledge path through AI-powered onboarding and structured district-based learning.
**Current focus:** Phase 7: First Course (all infrastructure + platform code complete)

## Current Position

Phase: 7 of 8 (First Course — next action)
Plan: 0 of 1 in current phase
Status: Ready to plan
Last activity: 2026-03-17 — Code review + bug fixes complete, pushed to GitHub

Progress: [████████░░] 85% (13/14 plans + Phase 8 extension)

## Performance Metrics

**Velocity:**
- Total plans completed: 14+
- Average duration: ~3 min
- Total execution time: ~0.7 hours

**By Phase:**

| Phase | Plans | Status |
|-------|-------|--------|
| 1. AWS Infrastructure | 3/3 | Complete |
| 2. OpenEdX Installation | 3/3 | Code complete |
| 3. Districts Setup | 1/1 | Code complete |
| 4. Theme Deployment | 2/2 | Code complete |
| 5. AI Onboarding | 2/2 | Code complete |
| 6. Partner Ecosystem | 2/2 | Code complete |
| 7. First Course | 0/1 | Not started |
| 8. Stack Extensions | 3/3 | Code complete |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Pre-Phase 1]: Tutor plugin over native install — single-command deployment
- [Pre-Phase 1]: No fork of openedx-platform — extend via plugins only
- [Phase 1]: Default VPC for Phase 1 simplicity
- [Phase 1]: MySQL 8.0 (OpenEdX default) over PostgreSQL
- [Phase 1]: IAM role (not hardcoded keys) for EC2 S3 access
- [Phase 1]: S3 lifecycle: Glacier at 30d, expire at 365d
- [Phase 8]: Discourse via SSO (OpenEdX as IDP, HMAC-SHA256)
- [Phase 8]: Opencast via LTI for video embedding in courses
- [Phase 8]: Presenton staff-only via Nginx basic auth (Phase 1)
- [Phase 8]: Secrets use CONFIG_UNIQUE for auto-generation

### Pending Todos

- Deploy to AWS (requires credentials + `terraform apply`)
- Create first foundation course in Studio (Phase 7)

### Blockers/Concerns

- AWS credentials needed before `terraform apply` can run
- me-central-1 region availability — may need eu-west-1 fallback
- Discourse API key must be generated manually post-install

## Session Continuity

Last session: 2026-03-17
Stopped at: Code review + bug fixes complete, all code pushed to GitHub
Resume file: None
