# CHRONOPOLI – Claude Code Master Context
# GSD Framework | OpenEdX on AWS/EKS | Dubai Blockchain Center

## WHAT THIS IS

You are building Chronopoli – a global knowledge platform for AI, blockchain,
governance, compliance, financial crime investigation, and enterprise risk.
Hosted by Dubai Blockchain Center (DBCC). Built on OpenEdX (Tutor), deployed
on AWS with auto-scaling via Kubernetes (EKS).

This file is your single source of truth. Read it completely before any task.

---

## REPOSITORY STRUCTURE

```
chronopoli/
├── CLAUDE.md                          ← YOU ARE HERE. Read first, always.
├── .planning/                         ← GSD state (managed by /gsd: commands)
│   ├── PROJECT.md                     ← Project context + decisions
│   ├── REQUIREMENTS.md                ← Scoped v1/v2 requirements
│   ├── ROADMAP.md                     ← 8 phases with plans
│   ├── STATE.md                       ← Living project memory
│   ├── config.json                    ← GSD workflow config
│   └── phases/                        ← Per-phase plan summaries
├── docs/
│   ├── 01-aws-infrastructure.md       ← AWS EC2 Phase 1 setup
│   ├── 02-tutor-installation.md       ← OpenEdX via Tutor (Docker)
│   ├── 04-districts-configuration.md  ← 6 Knowledge Districts setup
│   ├── 06-phase1-launch-checklist.md  ← Launch checklist
│   ├── DEPLOYMENT_HANDBOOK.md         ← 13-step engineer deployment guide
│   └── presenton-prompts.md           ← Per-district AI slide prompts
├── infrastructure/
│   ├── terraform/                     ← AWS IaC (EC2, RDS, S3, Route53, SES)
│   ├── extensions/                    ← Docker Compose for Opencast + Presenton
│   ├── nginx/                         ← Reverse proxy for video/slides subdomains
│   ├── kubernetes/                    ← EKS + Helm charts (Phase 2, future)
│   └── production.env.template        ← Environment variable template
├── tutor/
│   ├── config.yml                     ← Tutor base config
│   └── plugins/chronopoli/            ← Custom Tutor plugin (pip-installable)
├── theme/chronopoli-theme/            ← Custom OpenEdX dark/gold theme
├── plugins/
│   ├── ai-onboarding/                 ← 5-question district router (chronopoli_onboarding)
│   ├── partner-ecosystem/             ← Partner management (chronopoli_partners)
│   ├── discourse-sso/                 ← Discourse SSO endpoint (chronopoli_discourse_sso)
│   └── district-taxonomy/             ← Reserved for future district management
├── scripts/
│   ├── deploy.sh                      ← Docker/EC2 deployment
│   ├── setup-server.sh                ← EC2 provisioning (Docker, Tutor, firewall)
│   ├── configure-tutor.sh             ← Wire Tutor to AWS services
│   ├── setup-districts.sh             ← Create 6 districts + admin + demo courses
│   ├── setup-discourse.sh             ← Discourse installation + SSO config
│   ├── setup-discourse-categories.sh  ← District groups + categories
│   ├── setup-opencast.sh              ← Opencast video platform setup
│   ├── setup-presenton.sh             ← AI slide builder setup
│   ├── healthcheck.sh                 ← 8-category smoke test
│   └── backup.sh                      ← Database + media backup to S3
├── preview/                           ← Local landing page preview
│   ├── index.html
│   └── server.js
└── .github/workflows/
    ├── deploy-production.yml          ← CI/CD main → AWS
    └── deploy-staging.yml             ← CI/CD develop → staging
```

---

## THE PLATFORM: WHAT WE ARE BUILDING

### Core Concept
Chronopoli is NOT a course catalog. It is a "Global Knowledge City" – an
umbrella platform where regulators, law enforcement, banks, enterprises,
founders, and students all find what they need under one architecture.

### The 6 Knowledge Districts (OpenEdX Organizations)

| Code       | District Name        | Color   | Primary Audience              |
|------------|----------------------|---------|-------------------------------|
| CHRON-AI   | AI District          | #6C63FF | Enterprise leaders, CIOs      |
| CHRON-DA   | Digital Assets       | #F59E0B | Bankers, founders, regulators |
| CHRON-GOV  | Governance District  | #10B981 | Ministers, policymakers       |
| CHRON-COMP | Compliance District  | #3B82F6 | MLROs, compliance officers    |
| CHRON-INV  | Investigation        | #EF4444 | Law enforcement, FIUs         |
| CHRON-RISK | Risk & Trust         | #8B5CF6 | CROs, risk managers           |

### The 4 Learning Layers

| Layer | Tag             | Audience                       |
|-------|-----------------|--------------------------------|
| L1    | layer:entry     | Students, newcomers            |
| L2    | layer:professional | Executives, compliance teams |
| L3    | layer:institutional | Governments, regulators    |
| L4    | layer:influence | Thought leaders, researchers   |

### Partner Ecosystem
Partners are "Knowledge Partners" and host district-branded tracks.
- Founding: Ripple, Cardano, Hedera
- Strategic: Tether, Polygon, Chainlink
- Investigation: Chainalysis, TRM Labs, Elliptic
- AI: Microsoft AI, Google AI
- Institutional: Universities, think tanks, banks

---

## TECH STACK

### Core Platform
- **LMS**: OpenEdX (openedx/openedx-platform) via Tutor
- **Deployment Phase 1**: Docker on AWS EC2 t3.xlarge
- **Deployment Phase 2**: Kubernetes on AWS EKS (auto-scaling)
- **Database**: RDS MySQL 8.0 (or PostgreSQL via tutor-contrib-postgresql)
- **Cache**: ElastiCache Redis
- **Storage**: S3 (media, static, backups)
- **CDN**: CloudFront
- **DNS**: Route53

### Upstream Dependencies (DO NOT FORK, USE AS-IS)
- `github.com/openedx/openedx-platform` – pulled by Tutor automatically
- `github.com/overhangio/tutor` – our deployment engine
- `github.com/openedx/frontend-app-authoring` – Studio MFE (Tutor-managed)

### Our Custom Code (everything in this repo)
- Tutor Plugin: `tutor/plugins/chronopoli/`
- Theme: `theme/chronopoli-theme/`
- Django Apps: `plugins/ai-onboarding/`, `plugins/partner-ecosystem/`
- Infrastructure: `infrastructure/terraform/`, `infrastructure/kubernetes/`

---

## ARCHITECTURE DECISION: WHY NO FORK

We DO NOT fork openedx-platform. We extend it via the Tutor plugin system.
This means:
- `tutor upgrade` handles OpenEdX updates automatically
- Our code is decoupled from upstream changes
- We only maintain our plugins and theme

---

## CLOUD ARCHITECTURE (AUTO-SCALING)

### Phase 1 – EC2 Docker (Launch)
```
Route53 → CloudFront → EC2 t3.xlarge (Tutor Docker)
                    ↘ RDS MySQL
                    ↘ ElastiCache Redis
                    ↘ S3
Region: me-central-1 (UAE) or eu-west-1
Cost: ~$430/month
```

### Phase 2 – EKS Kubernetes (Scale)
```
Route53 → CloudFront → ALB Ingress → EKS Cluster
                                   ↘ LMS Deployment (HPA: 2-10 pods)
                                   ↘ CMS Deployment (HPA: 1-3 pods)
                                   ↘ Celery Workers (HPA: 2-8 pods)
                                   ↘ Forum Service
                                   ↘ RDS Aurora (Multi-AZ)
                                   ↘ ElastiCache Redis Cluster
                                   ↘ S3
Cost: $600-2,000/month (scales with traffic)
Auto-scaling: HPA on CPU/memory, KEDA on queue depth
```

---

## GSD WORKFLOW FOR THIS PROJECT

### How to start a new feature
```bash
# In Claude Code terminal:
/gsd:quick "Add partner onboarding flow for Ripple Digital Payments track"

# For larger features:
/gsd:new-milestone
# Then describe: "Build the AI onboarding questionnaire with district routing"
```

### Development phases GSD will create:
1. **Discuss** – Lock in requirements before writing code
2. **Plan** – Break into atomic tasks with verification steps
3. **Execute** – Build with fresh context per phase
4. **Verify** – Test against explicit goals
5. **Commit** – Atomic git commits per completed task

### GSD Config for this project
See `.planning/config.json` for full config. Key settings:
- Mode: interactive
- Granularity: standard (5-8 phases)
- Parallelization: enabled (3 concurrent agents)
- All gates: enabled (confirm before destructive actions)

### GSD Planning Files
- `.planning/PROJECT.md` – what we're building, core value, constraints, decisions
- `.planning/REQUIREMENTS.md` – 90 requirements mapped to 15 phases (33 v1 + 57 Master Doc)
- `.planning/ROADMAP.md` – 15 phases (8 core + 7 Master Document gap closure)
- `.planning/STATE.md` – current position, velocity, session continuity

---

## CURRENT STATUS (update this section constantly)

### Completed
- [x] Repository structure created
- [x] Terraform IaC – EC2, RDS, S3 (4 buckets), CloudFront, Route53 (5 subdomains), SES, IAM
- [x] Tutor configuration (config.yml)
- [x] Custom Tutor plugin – pip-installable package (pyproject.toml, CONFIG_UNIQUE secrets, patches, templates, init task)
- [x] AI Onboarding plugin – complete Django app (models, views, urls, admin, apps, signals, migrations)
- [x] Partner Ecosystem plugin – complete Django app (models, views, urls, admin, migrations)
- [x] Discourse SSO plugin – HMAC-SHA256 SSO handshake with district group assignment
- [x] Chronopoli dark/gold theme (CSS + header.html with Community/Video/Slides nav)
- [x] GitHub Actions CI/CD pipelines (deploy-production.yml, deploy-staging.yml)
- [x] 10 deployment/setup scripts (server, tutor, districts, discourse, opencast, presenton, healthcheck, backup, deploy, discourse-categories)
- [x] Docker Compose for extension services (Opencast + Presenton)
- [x] Nginx reverse proxy for video.chronopoli.io + slides.chronopoli.io
- [x] Deployment Handbook (13-step guide for engineer)
- [x] Production env template with all service variables
- [x] Presenton per-district brand prompts
- [x] GSD planning complete (.planning/ with 8 phases)
- [x] Code review + bug fixes (2026-03-17)
- [x] Shell script bug fixes — 52 bugs resolved (2026-03-20)
- [x] Master Document gap analysis — 7 gaps identified, 57 new requirements (2026-03-20)
- [x] GSD Phases 9–15 planned — REQUIREMENTS.md, ROADMAP.md, STATE.md updated (2026-03-20)

### In Progress
- [ ] Deploy to AWS (requires credentials + `terraform apply`)

### Next Milestones (Deploy-First)
1. **M1**: `terraform apply` + EC2 provisioning – all code ready, needs AWS credentials
2. **M2**: Phase 9 — CHRON-ET district (2h after deploy)
3. **M3**: Phase 10 — E-Commerce / Stripe (4–6 weeks)
4. **M4**: Phase 11 — Symposia Round Tables + Pipeline (8–10 weeks, commercial differentiator)
5. **M5**: Phase 12 — Company Academies (10–14 weeks, closes Ripple deal)
6. **M6**: Phase 13 — AI Tutor / Bedrock KB (6–8 weeks, platform moat)
7. **M7**: Phase 14+15 — Digital Twin + Partner Dashboard (6–8 + 3–4 weeks)

---

## KEY CONVENTIONS

### Git Branches
- `main` → production (auto-deploys to AWS)
- `develop` → staging
- `feature/milestone-name` → feature work

### Commit Format
```
feat(ai-onboarding): add district routing logic
fix(theme): correct mobile navigation padding
infra(kubernetes): add HPA config for LMS pods
docs(districts): update Compliance district course list
```

### Environment Variables (NEVER commit these)
```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
MYSQL_ROOT_PASSWORD
SECRET_KEY
SMTP_PASSWORD
```
All secrets go in AWS Secrets Manager + GitHub Secrets.

### Django App Naming
All Chronopoli Django apps prefixed: `chronopoli_`
- `chronopoli_onboarding` (plugins/ai-onboarding/)
- `chronopoli_partners` (plugins/partner-ecosystem/)
- `chronopoli_discourse_sso` (plugins/discourse-sso/)
- `chronopoli_ecommerce` (plugins/ecommerce/) — Phase 10
- `chronopoli_symposia` (plugins/symposia/) — Phase 11
- `chronopoli_academy` (plugins/company-academy/) — Phase 12
- `chronopoli_ai_tutor` (plugins/ai-tutor/) — Phase 13
- `chronopoli_masterclass` (plugins/masterclass/) — Phase 14
- `chronopoli_discourse_sso` (plugins/discourse-sso/)

---

## WHEN CLAUDE CODE READS THIS FILE

1. Read CLAUDE.md completely before starting any task
2. Read `.planning/STATE.md` for current position and context
3. Read `.planning/PROJECT.md` for requirements and decisions
4. Check `CURRENT STATUS` section above
5. Never modify CLAUDE.md mid-task (read-only context)
6. Use `/gsd:plan-phase N` to plan work, `/gsd:execute-phase N` to build

---

## USEFUL COMMANDS

```bash
# Start OpenEdX locally
tutor local start -d

# View LMS logs
tutor local logs -f lms

# Run Django shell
tutor local do exec lms ./manage.py lms shell

# Deploy to production
./scripts/deploy.sh production

# Deploy to Kubernetes (Phase 2)
./scripts/deploy-k8s.sh production

# Consolidate upstream OpenEdX references
./scripts/consolidate.sh

# GSD commands (framework installed globally)
/gsd:progress              # Show current state
/gsd:plan-phase 1          # Plan Phase 1
/gsd:execute-phase 1       # Execute Phase 1
/gsd:verify-work 1         # Verify Phase 1 deliverables
/gsd:quick "description"   # Fast ad-hoc task
/gsd:new-milestone          # Start next milestone
```

---

## LINKS

- OpenEdX Platform: https://github.com/openedx/openedx-platform
- Tutor Docs: https://docs.tutor.edly.io
- OpenEdX Docs: https://docs.openedx.org
- GSD Framework: https://github.com/gsd-build/get-shit-done
- Chronopoli Strategy PDF: /docs/source/chronopoli_strategy_detailed.pdf
- AWS Console: https://console.aws.amazon.com
- Region: me-central-1 (UAE)
