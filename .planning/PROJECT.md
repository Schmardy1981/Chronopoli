# Chronopoli

## What This Is

Chronopoli is a global knowledge platform for AI, blockchain, governance, compliance, financial crime investigation, and enterprise risk — hosted by Dubai Blockchain Center (DBCC). Built on OpenEdX via Tutor, deployed on AWS with a Phase 1 EC2/Docker architecture scaling to EKS/Kubernetes in Phase 2. It organizes knowledge into 6 "Knowledge Districts" with personalized AI-driven onboarding and a partner ecosystem for industry leaders like Ripple, Chainalysis, and Microsoft AI.

## Core Value

Professionals in regulated industries (compliance, law enforcement, governance, risk) can discover the right knowledge path through AI-powered onboarding and structured district-based learning — all under one platform rather than scattered across dozens of providers.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

- ✓ Tutor plugin structure — pip-installable with proper entry points (v0.1)
- ✓ AI onboarding Django app — models, views, URLs, admin, migrations, templates (v0.1)
- ✓ Partner ecosystem Django app — models, views, URLs, admin, migrations, templates (v0.1)
- ✓ Terraform IaC — EC2, RDS, S3, CloudFront, IAM (v0.1)
- ✓ CI/CD pipelines — GitHub Actions for production and staging (v0.1)
- ✓ Dark/gold theme CSS — design tokens, district cards, onboarding UI (v0.1)

### Active

<!-- Current scope. Building toward these. -->

- [ ] OpenEdX running locally via `tutor local start` with Chronopoli plugin
- [ ] 6 Knowledge Districts created as OpenEdX organizations
- [ ] AI onboarding questionnaire functional end-to-end
- [ ] Theme HTML templates (header, footer, homepage) applied in OpenEdX
- [ ] Deploy to AWS EC2 with `./scripts/deploy.sh production`
- [ ] First partner track live (Ripple or Cardano)
- [ ] Partner admin portal for content management

### Out of Scope

<!-- Explicit boundaries. Includes reasoning to prevent re-adding. -->

- Forking openedx-platform — Tutor plugin system handles all customization without fork maintenance burden
- Kubernetes/EKS (Phase 2) — deferred until traffic justifies the complexity ($600+/mo vs $430/mo)
- Mobile native app — OpenEdX responsive web + mobile REST API sufficient for launch
- Real-time chat — Circle community platform handles this via CNAME integration
- Custom video hosting — S3 + CloudFront sufficient; Vimeo/YouTube embeds for partners
- Multi-language i18n — English-only for v1; audience is global but professional English-speaking

## Context

- **Platform**: OpenEdX (Tutor deployment) — the only officially supported deployment method since Redwood release (2024+)
- **Host**: Dubai Blockchain Center (DBCC) — provides institutional credibility and partner network
- **Target audience**: Senior professionals — regulators, MLROs, CROs, law enforcement, enterprise leaders. Not students looking for MOOCs.
- **Theme**: Dark background with gold accents (Dubai aesthetic). 6 district accent colors for visual navigation.
- **Existing code**: Consolidation session completed — all Django apps, Tutor plugin, Terraform, CI/CD, and theme CSS built. Missing: integration testing, theme HTML, and actual AWS deployment.
- **Upstream dependencies**: openedx-platform, tutor, tutor-mfe, frontend-app-authoring — all cloned to `.upstream/` for reference, never forked.

## Constraints

- **Tech stack**: OpenEdX + Tutor (Docker) — non-negotiable, DBCC decision
- **AWS region**: me-central-1 (UAE) for data residency, fallback eu-west-1
- **Budget**: ~$430/mo Phase 1 (EC2), scaling to $600-2000/mo Phase 2 (EKS)
- **No fork policy**: All customization via Tutor plugins, Django apps, and themes
- **Django naming**: All apps prefixed `chronopoli_` (chronopoli_onboarding, chronopoli_partners)
- **Security**: Secrets in AWS Secrets Manager + GitHub Secrets, never committed

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Tutor over native OpenEdX install | Single-command deployment, plugin system, automatic upgrades | ✓ Good |
| No fork of openedx-platform | Decouples from upstream churn, Tutor handles updates | ✓ Good |
| EC2 Docker before EKS | Lower cost for launch ($430 vs $600+), simpler ops | — Pending |
| MySQL over PostgreSQL | OpenEdX default, Tutor native support | — Pending |
| 6 districts as OpenEdX orgs | Maps cleanly to OpenEdX's multi-org model | ✓ Good |
| AI onboarding as Django app | Server-rendered, no external AI dependency, works offline | ✓ Good |
| Dark/gold theme | Matches DBCC Dubai aesthetic, differentiates from OpenEdX default | — Pending |

---
*Last updated: 2026-03-17 after consolidation session*
