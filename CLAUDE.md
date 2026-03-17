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
│   ├── ROADMAP.md                     ← 7 phases with plans
│   ├── STATE.md                       ← Living project memory
│   ├── config.json                    ← GSD workflow config
│   └── GAP_ANALYSIS.md               ← Component status audit
├── docs/
│   ├── 01-aws-infrastructure.md       ← AWS EC2 Phase 1 setup
│   ├── 02-tutor-installation.md       ← OpenEdX via Tutor (Docker)
│   ├── 03-kubernetes-scaling.md       ← EKS Phase 2 auto-scaling
│   ├── 04-districts-configuration.md  ← 6 Knowledge Districts setup
│   ├── 05-partner-onboarding.md       ← Partner management workflow
│   └── 06-phase1-launch-checklist.md  ← Launch checklist
├── infrastructure/
│   ├── terraform/                     ← AWS IaC (EC2 Phase 1)
│   └── kubernetes/                    ← EKS + Helm charts (Phase 2)
├── tutor/
│   ├── config.yml                     ← Tutor base config
│   └── plugins/chronopoli/            ← Custom Tutor plugin
├── theme/chronopoli-theme/            ← Custom OpenEdX dark/gold theme
├── plugins/
│   ├── ai-onboarding/                 ← 5-question district router
│   ├── partner-ecosystem/             ← Partner management Django app
│   └── district-taxonomy/             ← 6 districts as OpenEdX orgs
├── scripts/
│   ├── deploy.sh                      ← Docker/EC2 deployment
│   ├── deploy-k8s.sh                  ← Kubernetes deployment
│   └── consolidate.sh                 ← Pulls OpenEdX upstream refs
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
- `.planning/REQUIREMENTS.md` – 33 v1 requirements mapped to 7 phases
- `.planning/ROADMAP.md` – 7 phases with 14 plans total
- `.planning/STATE.md` – current position, velocity, session continuity

---

## CURRENT STATUS (update this section constantly)

### Completed
- [x] Repository structure created
- [x] AWS infrastructure documented (Phase 1 EC2)
- [x] Tutor configuration (config.yml)
- [x] Custom Tutor plugin – full pip-installable package (pyproject.toml, tutorchronopoli/, patches/, templates/)
- [x] AI Onboarding plugin – complete Django app (models, views, urls, admin, apps, signals, migrations, Mako templates)
- [x] Partner Ecosystem plugin – complete Django app (models, views, urls, admin, migrations, Mako templates)
- [x] Chronopoli dark/gold theme (CSS)
- [x] GitHub Actions CI/CD pipelines (deploy-production.yml, deploy-staging.yml)
- [x] Deployment script (deploy.sh)
- [x] 6 Districts configuration guide
- [x] Phase 1 launch checklist
- [x] Terraform IaC skeleton (main.tf, rds.tf, s3.tf, cloudfront.tf, variables.tf, outputs.tf)
- [x] Gap analysis document (.planning/GAP_ANALYSIS.md)
- [x] Upstream repos cloned for reference (.upstream/tutor-core, tutor-mfe, openedx-platform)
- [x] .gitignore configured
- [x] GSD planning config + roadmap (.planning/)

### In Progress
- [ ] Kubernetes/EKS setup (Phase 2 auto-scaling)
- [ ] Theme HTML templates (header, footer, homepage – CSS exists, HTML needed)
- [ ] District taxonomy management command
- [ ] Missing docs (03-custom-theme.md, 05-partner-onboarding.md)

### Next Milestones
1. **M1**: AWS infra + OpenEdX running (EC2) – Terraform ready, needs `terraform apply`
2. **M2**: Custom theme live + Districts configured
3. **M3**: AI onboarding questionnaire working – Django app complete, needs integration test
4. **M4**: First partner track (Ripple or Cardano) – Partner app complete, needs data
5. **M5**: Kubernetes migration + auto-scaling

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
- `chronopoli_onboarding`
- `chronopoli_partners`
- `chronopoli_districts`

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
