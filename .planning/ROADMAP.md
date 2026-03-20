# Roadmap: Chronopoli

## Overview

Chronopoli launches in 15 phases. Phases 1–8: core platform (infrastructure, OpenEdX, districts, theme, onboarding, partners, content, stack extensions). Phases 9–15: Master Document vision (CHRON-ET district, Stripe e-commerce, Symposia round tables, Company Academies, AI Tutor, Digital Twins, Partner Dashboard). Deploy-first: terraform apply before Phases 9+.

## Phases

- [x] **Phase 1: AWS Infrastructure** - Provision EC2, RDS, S3, CloudFront via Terraform
- [ ] **Phase 2: OpenEdX Installation** - Tutor install with Chronopoli plugin on EC2
- [ ] **Phase 3: Districts Setup** - Create 6 Knowledge Districts as OpenEdX organizations
- [ ] **Phase 4: Theme Deployment** - Apply Chronopoli dark/gold theme with HTML templates
- [ ] **Phase 5: AI Onboarding** - Wire onboarding questionnaire into registration flow
- [ ] **Phase 6: Partner Ecosystem** - Integrate partner app and create first partner org
- [ ] **Phase 7: First Course** - Create and publish foundation course in Studio
- [ ] **Phase 9: Emerging Tech District** - Add CHRON-ET (7th district) across all layers
- [ ] **Phase 10: E-Commerce / Stripe** - Paid courses, subscriptions, 70/30 creator split
- [ ] **Phase 11: Symposia Round Tables** - Live IVS sessions + 8-step Step Functions pipeline
- [ ] **Phase 12: Company Academy** - Partner subdomains, pathways, badges, talent pipeline
- [ ] **Phase 13: AI Tutor** - Bedrock Knowledge Base RAG + floating chat widget
- [ ] **Phase 14: Digital Twin / Master Class** - PDF→knowledge→voice clone→avatar→live session
- [ ] **Phase 15: Partner Dashboard** - Analytics, intelligence reports, Chart.js UI

## Phase Details

### Phase 1: AWS Infrastructure
**Goal**: All AWS resources provisioned and accessible
**Depends on**: Nothing (first phase)
**Requirements**: INFRA-01, INFRA-02, INFRA-03, INFRA-04, INFRA-05, INFRA-06
**Success Criteria** (what must be TRUE):
  1. EC2 t3.xlarge is running with Elastic IP and SSH access works
  2. RDS MySQL endpoint is reachable from EC2
  3. S3 buckets exist and EC2 IAM role can read/write to them
  4. CloudFront distribution serves learn.chronopoli.io
  5. `terraform plan` shows no pending changes
**Plans**: 3 plans

Plans:
- [x] 01-01: Validate EC2 + security groups + IAM Terraform config
- [x] 01-02: Validate RDS + S3 Terraform config
- [x] 01-03: Validate CloudFront + SSL Terraform config

### Phase 2: OpenEdX Installation
**Goal**: OpenEdX LMS and Studio running on EC2 with Chronopoli plugin
**Depends on**: Phase 1
**Requirements**: PLAT-01, PLAT-02, PLAT-03, PLAT-04, PLAT-05
**Success Criteria** (what must be TRUE):
  1. `tutor local start -d` runs successfully on EC2
  2. LMS loads at learn.chronopoli.io
  3. Studio loads at studio.chronopoli.io
  4. Admin user can log in to /admin
  5. Chronopoli plugin is enabled and settings are applied
**Plans**: 3 plans

Plans:
- [ ] 02-01: Install Docker + Tutor on EC2, configure tutor config.yml
- [ ] 02-02: Install Chronopoli Tutor plugin, build images, run init
- [ ] 02-03: Configure external services (RDS, Redis, S3, SES), verify health

### Phase 3: Districts Setup
**Goal**: 6 Knowledge Districts exist as OpenEdX organizations with admin users
**Depends on**: Phase 2
**Requirements**: DIST-01, DIST-02, DIST-03, DIST-04
**Success Criteria** (what must be TRUE):
  1. All 6 orgs visible in /admin/organizations/
  2. New course can be created under any district org in Studio
  3. District admin users have staff access
**Plans**: 1 plan

Plans:
- [ ] 03-01: Run district init script, create admin users, verify in admin panel

### Phase 4: Theme Deployment
**Goal**: Chronopoli dark/gold theme visible on LMS with proper navigation
**Depends on**: Phase 2
**Requirements**: THEME-01, THEME-02, THEME-03, THEME-04, THEME-05
**Success Criteria** (what must be TRUE):
  1. LMS homepage shows Chronopoli branding (dark background, gold accents)
  2. Header has Chronopoli logo/wordmark and navigation links
  3. 6 district cards displayed with correct colors
  4. Mobile layout works at 768px breakpoint
  5. Course cards use Chronopoli styling
**Plans**: 2 plans

Plans:
- [ ] 04-01: Create HTML templates (header.html, footer.html, index.html) for OpenEdX theme
- [ ] 04-02: Deploy theme to Tutor, rebuild images, verify visually

### Phase 5: AI Onboarding
**Goal**: New users complete onboarding questionnaire and get district recommendations
**Depends on**: Phase 3
**Requirements**: ONBD-01, ONBD-02, ONBD-03, ONBD-04, ONBD-05, ONBD-06
**Success Criteria** (what must be TRUE):
  1. Registration redirects to /chronopoli/onboarding/
  2. 5 questions render and step through correctly
  3. Results page shows correct primary district based on answers
  4. OnboardingProfile record exists in database after completion
  5. API at /chronopoli/api/onboarding/status/ returns correct JSON
**Plans**: 2 plans

Plans:
- [ ] 05-01: Wire signals, test form submission, verify database writes
- [ ] 05-02: Integration test full registration → onboarding → results flow

### Phase 6: Partner Ecosystem
**Goal**: Partner management working, first partner organization ready for content
**Depends on**: Phase 3
**Requirements**: PART-01, PART-02, PART-03, PART-04, PART-05
**Success Criteria** (what must be TRUE):
  1. Partners can be created via Django admin with tier and districts
  2. Partner tracks link to OpenEdX courses
  3. /chronopoli/partners/ shows active partners
  4. Partner detail page shows published tracks
**Plans**: 2 plans

Plans:
- [ ] 06-01: Create seed data (Ripple, Cardano, Chainalysis), test admin CRUD
- [ ] 06-02: Verify partner pages render correctly with theme styling

### Phase 7: First Course
**Goal**: At least one foundation course is live and enrollable
**Depends on**: Phase 4
**Requirements**: CONT-01, CONT-02, CONT-03
**Success Criteria** (what must be TRUE):
  1. Course exists in Studio under CHRON-AI or CHRON-DA org
  2. Course has at least 1 section with content
  3. Test user can enroll, view content, and complete the course
**Plans**: 1 plan

Plans:
- [ ] 07-01: Create course in Studio, add content, test enrollment and completion

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7
(Phases 3-4 can run in parallel after Phase 2; Phases 5-6 can run in parallel after Phase 3)

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. AWS Infrastructure | 3/3 | Complete | 2026-03-17 |
| 2. OpenEdX Installation | 3/3 | Code complete (deploy pending) | 2026-03-17 |
| 3. Districts Setup | 1/1 | Code complete (deploy pending) | 2026-03-17 |
| 4. Theme Deployment | 2/2 | Code complete (deploy pending) | 2026-03-17 |
| 5. AI Onboarding | 2/2 | Code complete (deploy pending) | 2026-03-17 |
| 6. Partner Ecosystem | 2/2 | Code complete (deploy pending) | 2026-03-17 |
| 7. First Course | 0/1 | Not started | - |
| 8. Stack Extensions | 3/3 | Code complete (deploy pending) | 2026-03-17 |

### Phase 9: Emerging Tech District (CHRON-ET)
**Goal**: Add 7th Knowledge District across all platform layers
**Depends on**: None (standalone)
**Requirements**: DIST-ET-01 through DIST-ET-07
**Success Criteria**:
  1. CHRON-ET appears in plugin CONFIG_DEFAULTS with color #06B6D4
  2. setup-districts.sh creates CHRON-ET org and ET-101 demo course
  3. Discourse setup creates emerging-tech-district group
  4. AI onboarding includes Emerging Technologies option
  5. Theme renders 7th district card with cyan color
**Plans**: 2 plans

Plans:
- [ ] 09-01: Backend config (plugin, scripts, onboarding, discourse SSO, init task)
- [ ] 09-02: Theme CSS + presenton prompts + verify 7 districts render

### Phase 10: E-Commerce / Stripe
**Goal**: Paid courses via Stripe with tiered pricing and creator revenue splits
**Depends on**: v1 deployed (Phases 1–8)
**Requirements**: ECOM-01 through ECOM-08
**Success Criteria**:
  1. Stripe checkout → webhook → auto-enrollment works end-to-end
  2. Partner gets 70% via Stripe Connect
  3. Corporate subscription creates with N seats
  4. SSM Parameter Store holds Stripe keys
**Plans**: 4 plans

Plans:
- [ ] 10-01: Django app chronopoli_ecommerce (models, admin, migrations)
- [ ] 10-02: Stripe checkout flow (stripe_client.py, views, webhook)
- [ ] 10-03: Team subscriptions + Stripe Connect (partner revenue split)
- [ ] 10-04: Terraform SSM + plugin wiring + healthcheck

### Phase 11: Symposia — Round Tables + Automation Pipeline
**Goal**: Live round tables via IVS with 8-step automated content pipeline
**Depends on**: Phase 9
**Requirements**: SYMP-01 through SYMP-10
**Success Criteria**:
  1. Schedule → Stream → Recording in S3 → Pipeline → 7 outputs → Approve → Publish
  2. All 8 Lambda functions execute in Step Functions state machine
  3. Opinion paper PDF generated via WeasyPrint
  4. Single human approval touchpoint in Django admin
**Plans**: 5 plans

Plans:
- [ ] 11-01: Django app chronopoli_symposia (models, admin, views, migrations)
- [ ] 11-02: Terraform IVS + S3 recording + EventBridge
- [ ] 11-03: Terraform Step Functions + 8 Lambda functions
- [ ] 11-04: Terraform SQS + Celery approval polling
- [ ] 11-05: Plugin wiring + end-to-end integration test

### Phase 12: Company Academy Tenant Model
**Goal**: Partners operate branded sub-academies with pathways, badges, talent pipeline
**Depends on**: Phase 10
**Requirements**: ACAD-01 through ACAD-10
**Success Criteria**:
  1. ripple.chronopoli.io renders partner-branded academy
  2. Pathway completion → badge award → auto job application
  3. SES email to partner HR with applicant details
  4. Wildcard DNS + Nginx resolve partner subdomains
**Plans**: 5 plans

Plans:
- [ ] 12-01: Extend Partner model + migration 0002
- [ ] 12-02: Django app chronopoli_academy (Pathway, Badge, UserBadge + admin)
- [ ] 12-03: Subdomain middleware + academy views + templates
- [ ] 12-04: Talent pipeline (jobs, auto-apply signal, SES)
- [ ] 12-05: Terraform wildcard DNS/SSL + Nginx + plugin wiring

### Phase 13: AI Tutor — Bedrock Knowledge Base
**Goal**: Conversational AI tutor powered by Bedrock RAG, personalized, SSE streaming
**Depends on**: Phase 11 (content feeds knowledge base)
**Requirements**: TUTOR-01 through TUTOR-08
**Success Criteria**:
  1. Chat widget on every LMS page, streams answers
  2. Responses cite Symposia papers and course content
  3. Personalized to user's district/layer from onboarding profile
  4. Bedrock Knowledge Base syncs from S3 automatically
**Plans**: 4 plans

Plans:
- [ ] 13-01: Django app chronopoli_ai_tutor (models, SSE view, bedrock_client)
- [ ] 13-02: Terraform Bedrock KB + OpenSearch Serverless + S3
- [ ] 13-03: Floating sidebar widget (JS/CSS) + theme integration
- [ ] 13-04: Plugin wiring + ingestion task + end-to-end test

### Phase 14: Digital Twin / Master Class
**Goal**: Experts create AI digital twins for interactive masterclass experiences
**Depends on**: Phase 11 (IVS reuse), Phase 13 (knowledge base)
**Requirements**: TWIN-01 through TWIN-08
**Success Criteria**:
  1. PDF upload → Textract → Claude analysis → interview questions
  2. ElevenLabs voice clone + HeyGen avatar video
  3. Live masterclass via IVS with post-session Symposia pipeline
**Plans**: 4 plans

Plans:
- [ ] 14-01: Django app chronopoli_masterclass (models, admin, migrations)
- [ ] 14-02: Document processing (Textract + Claude + question generation)
- [ ] 14-03: ElevenLabs voice + HeyGen avatar integration
- [ ] 14-04: Plugin wiring + IVS reuse + integration test

### Phase 15: Partner Intelligence Dashboard
**Goal**: Partners see analytics, intelligence reports, talent metrics
**Depends on**: Phase 11 + Phase 12
**Requirements**: DASH-01 through DASH-06
**Success Criteria**:
  1. Dashboard at /chronopoli/partners/<slug>/dashboard/ with Chart.js
  2. Weekly SES report email to partner contacts
  3. Intelligence reports from Symposia pipeline visible
**Plans**: 3 plans

Plans:
- [ ] 15-01: Dashboard views + analytics.py + Chart.js templates
- [ ] 15-02: Weekly SES report task + Celery beat schedule
- [ ] 15-03: URL wiring + access control + integration test

## Progress

**Execution Order:**
Phases 1–8: sequential (core platform). Phases 9–15: dependency-driven (see plan).
Prerequisite: terraform apply + v1 live before Phases 9+.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. AWS Infrastructure | 3/3 | Complete | 2026-03-17 |
| 2. OpenEdX Installation | 3/3 | Code complete (deploy pending) | 2026-03-17 |
| 3. Districts Setup | 1/1 | Code complete (deploy pending) | 2026-03-17 |
| 4. Theme Deployment | 2/2 | Code complete (deploy pending) | 2026-03-17 |
| 5. AI Onboarding | 2/2 | Code complete (deploy pending) | 2026-03-17 |
| 6. Partner Ecosystem | 2/2 | Code complete (deploy pending) | 2026-03-17 |
| 7. First Course | 0/1 | Not started | - |
| 8. Stack Extensions | 3/3 | Code complete (deploy pending) | 2026-03-17 |
| 9. CHRON-ET District | 0/2 | Not started | - |
| 10. E-Commerce / Stripe | 0/4 | Not started | - |
| 11. Symposia Pipeline | 0/5 | Not started | - |
| 12. Company Academy | 0/5 | Not started | - |
| 13. AI Tutor | 0/4 | Not started | - |
| 14. Digital Twin | 0/4 | Not started | - |
| 15. Partner Dashboard | 0/3 | Not started | - |

**Note:** Phases 9–15 close all gaps from the Master Document.
All code-complete phases need AWS credentials + `terraform apply` to go live.
