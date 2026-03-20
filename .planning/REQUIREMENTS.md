# Requirements: Chronopoli

**Defined:** 2026-03-17
**Core Value:** Professionals in regulated industries can discover the right knowledge path through AI-powered onboarding and structured district-based learning.

## v1 Requirements

Requirements for initial production launch at learn.chronopoli.io.

### Infrastructure

- [ ] **INFRA-01**: OpenEdX runs via Tutor on AWS EC2 t3.xlarge (Ubuntu 22.04)
- [ ] **INFRA-02**: RDS MySQL accessible from EC2 with encrypted storage
- [ ] **INFRA-03**: S3 buckets created for media, static assets, and backups
- [ ] **INFRA-04**: CloudFront CDN serves learn.chronopoli.io with valid SSL
- [ ] **INFRA-05**: Route53 DNS configured for learn/studio subdomains
- [ ] **INFRA-06**: deploy.sh deploys from GitHub to production in one command

### Platform

- [ ] **PLAT-01**: Tutor plugin installs via pip and enables Chronopoli settings
- [ ] **PLAT-02**: LMS accessible at learn.chronopoli.io with Chronopoli branding
- [ ] **PLAT-03**: Studio accessible at studio.chronopoli.io for course authoring
- [ ] **PLAT-04**: Admin user can log in to /admin and manage platform
- [ ] **PLAT-05**: Email delivery works (registration, password reset) via AWS SES

### Districts

- [ ] **DIST-01**: 6 Knowledge Districts exist as OpenEdX organizations
- [ ] **DIST-02**: Each district has its own color, name, and description
- [ ] **DIST-03**: Courses can be created under any district org in Studio
- [ ] **DIST-04**: District admin users have staff access to their org

### Theme

- [ ] **THEME-01**: Chronopoli dark/gold theme applied to LMS homepage
- [ ] **THEME-02**: Global header shows Chronopoli branding and navigation
- [ ] **THEME-03**: District cards displayed on homepage with correct colors
- [ ] **THEME-04**: Theme is mobile-responsive (breakpoints at 768px)
- [ ] **THEME-05**: Course cards styled with Chronopoli design tokens

### AI Onboarding

- [ ] **ONBD-01**: New users redirected to /chronopoli/onboarding/ after registration
- [ ] **ONBD-02**: 5-question questionnaire renders with step-by-step progression
- [ ] **ONBD-03**: Answers determine primary district, secondary districts, and learning layer
- [ ] **ONBD-04**: Results page shows personalized district + course recommendations
- [ ] **ONBD-05**: OnboardingProfile saved to database for each user
- [ ] **ONBD-06**: API endpoint returns onboarding status for current user

### Partners

- [ ] **PART-01**: Partner model stores name, tier, districts, and OpenEdX org code
- [ ] **PART-02**: Partner tracks link to OpenEdX courses via course_key
- [ ] **PART-03**: Partners page lists all active partners with their tracks
- [ ] **PART-04**: Partner detail page shows description and published tracks
- [ ] **PART-05**: Admin can create/edit partners and tracks via Django admin

### Content

- [ ] **CONT-01**: At least 1 foundation course exists in Studio (CHRON-AI or CHRON-DA)
- [ ] **CONT-02**: Course is enrollable and completable by test users
- [ ] **CONT-03**: Course tagged with learning layer (layer:entry)

### Emerging Tech District (Phase 9)

- [ ] **DIST-ET-01**: CHRON-ET organization exists in OpenEdX with code, name, color (#06B6D4)
- [ ] **DIST-ET-02**: Plugin CONFIG_DEFAULTS includes CHRON-ET in CHRONOPOLI_DISTRICTS
- [ ] **DIST-ET-03**: setup-districts.sh creates CHRON-ET org and demo course ET-101
- [ ] **DIST-ET-04**: setup-discourse-categories.sh creates CHRON-ET group and categories
- [ ] **DIST-ET-05**: AI onboarding quiz includes Emerging Technologies option
- [ ] **DIST-ET-06**: Theme CSS includes .district-et styles with cyan accent
- [ ] **DIST-ET-07**: Tutor init task creates CHRON-ET organization

### E-Commerce / Stripe (Phase 10)

- [ ] **ECOM-01**: Tutor ecommerce plugin activated and configured
- [ ] **ECOM-02**: Stripe payment processor configured (replaces CyberSource)
- [ ] **ECOM-03**: Course pricing tiers exist for L1-L4 layers
- [ ] **ECOM-04**: Stripe Connect enabled for partner revenue split (70/30)
- [ ] **ECOM-05**: Corporate team subscription model via Stripe billing
- [ ] **ECOM-06**: SSM Parameter Store holds Stripe keys (no hardcoded secrets)
- [ ] **ECOM-07**: Checkout flow completes end-to-end (cart → payment → enrollment)
- [ ] **ECOM-08**: Webhook handler processes Stripe events

### Symposia Round Tables (Phase 11)

- [ ] **SYMP-01**: Django app chronopoli_symposia with RoundTable, Invitation, Output models
- [ ] **SYMP-02**: Amazon IVS channel creation and management for live round tables
- [ ] **SYMP-03**: IVS auto-records to S3 on session end
- [ ] **SYMP-04**: EventBridge rule triggers Step Functions on IVS recording_end
- [ ] **SYMP-05**: 8-step Step Functions state machine (transcribe → analyze → generate → publish)
- [ ] **SYMP-06**: Lambda functions for each pipeline step with proper IAM roles
- [ ] **SYMP-07**: SQS queue for Django approval flow (human-in-the-loop)
- [ ] **SYMP-08**: Single human approval touchpoint before content goes live
- [ ] **SYMP-09**: Opinion papers generated as PDF (WeasyPrint) and stored in S3
- [ ] **SYMP-10**: RoundTable lifecycle managed via Django admin

### Company Academy (Phase 12)

- [ ] **ACAD-01**: Partner model extended with subdomain, Stripe, branding fields
- [ ] **ACAD-02**: Subdomain routing middleware resolves partner.chronopoli.io
- [ ] **ACAD-03**: LearningPathway model groups courses into structured progressions
- [ ] **ACAD-04**: Badge model implements Open Badges 2.0 specification
- [ ] **ACAD-05**: Badges auto-awarded on CERTIFICATE_CREATED signal
- [ ] **ACAD-06**: PartnerJobPosting and JobApplication models enable talent pipeline
- [ ] **ACAD-07**: Auto-submit applications when credentials match job requirements
- [ ] **ACAD-08**: Partner Academy homepage renders with partner branding
- [ ] **ACAD-09**: Nginx wildcard subdomain config for *.chronopoli.io
- [ ] **ACAD-10**: SES notifications sent to partner HR on new qualified applicants

### AI Tutor (Phase 13)

- [ ] **TUTOR-01**: Django app chronopoli_ai_tutor with TutorSession, TutorMessage models
- [ ] **TUTOR-02**: Amazon Bedrock Knowledge Base configured with S3 data source
- [ ] **TUTOR-03**: OpenSearch Serverless collection for vector storage
- [ ] **TUTOR-04**: SSE streaming response endpoint for real-time AI chat
- [ ] **TUTOR-05**: System prompt personalized using OnboardingProfile (district, layer)
- [ ] **TUTOR-06**: Floating sidebar widget injected into LMS theme
- [ ] **TUTOR-07**: S3 knowledge paths organized by content type
- [ ] **TUTOR-08**: Knowledge base ingestion triggered after new content approved

### Digital Twin / Master Class (Phase 14)

- [ ] **TWIN-01**: Django app chronopoli_masterclass with DigitalTwin model
- [ ] **TWIN-02**: Expert PDF upload triggers Textract extraction + Claude analysis
- [ ] **TWIN-03**: Interview questions auto-generated from extracted expertise
- [ ] **TWIN-04**: ElevenLabs voice cloning from optional audio sample
- [ ] **TWIN-05**: HeyGen avatar video generation from text script
- [ ] **TWIN-06**: Live masterclass session via IVS (reuse Symposia infrastructure)
- [ ] **TWIN-07**: Post-session outputs processed through Symposia pipeline
- [ ] **TWIN-08**: Digital twin profile page with generated videos and Q&A

### Partner Dashboard (Phase 15)

- [ ] **DASH-01**: Partner dashboard views in chronopoli_partners app
- [ ] **DASH-02**: Academy analytics: enrollments, completions, badges per partner
- [ ] **DASH-03**: Intelligence report delivery from Symposia pipeline outputs
- [ ] **DASH-04**: Chart.js frontend for visual analytics
- [ ] **DASH-05**: Weekly SES report email to partner contacts
- [ ] **DASH-06**: Dashboard accessible at /chronopoli/partners/<slug>/dashboard/

## v2 Requirements

Deferred to future milestones.

### Auto-Scaling

- **SCALE-01**: Platform runs on EKS with HPA for LMS/CMS/workers
- **SCALE-02**: Auto-scales from 2-10 LMS pods based on CPU/memory
- **SCALE-03**: Helm chart packages full Chronopoli deployment

## Out of Scope

| Feature | Reason |
|---------|--------|
| openedx-platform fork | Plugin system handles all customization |
| Kubernetes/EKS | Deferred to v2 after traffic justifies cost |
| Mobile native app | Responsive web + REST API sufficient |
| Multi-language | English-only for professional audience |
| n8n workflow | AWS Step Functions replaces n8n (AWS-native) |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| INFRA-01 | Phase 1 | Complete |
| INFRA-02 | Phase 1 | Complete |
| INFRA-03 | Phase 1 | Complete |
| INFRA-04 | Phase 1 | Complete |
| INFRA-05 | Phase 1 | Complete |
| INFRA-06 | Phase 1 | Complete |
| PLAT-01 | Phase 2 | Pending |
| PLAT-02 | Phase 2 | Pending |
| PLAT-03 | Phase 2 | Pending |
| PLAT-04 | Phase 2 | Pending |
| PLAT-05 | Phase 2 | Pending |
| DIST-01 | Phase 3 | Pending |
| DIST-02 | Phase 3 | Pending |
| DIST-03 | Phase 3 | Pending |
| DIST-04 | Phase 3 | Pending |
| THEME-01 | Phase 4 | Pending |
| THEME-02 | Phase 4 | Pending |
| THEME-03 | Phase 4 | Pending |
| THEME-04 | Phase 4 | Pending |
| THEME-05 | Phase 4 | Pending |
| ONBD-01 | Phase 5 | Pending |
| ONBD-02 | Phase 5 | Pending |
| ONBD-03 | Phase 5 | Pending |
| ONBD-04 | Phase 5 | Pending |
| ONBD-05 | Phase 5 | Pending |
| ONBD-06 | Phase 5 | Pending |
| PART-01 | Phase 6 | Pending |
| PART-02 | Phase 6 | Pending |
| PART-03 | Phase 6 | Pending |
| PART-04 | Phase 6 | Pending |
| PART-05 | Phase 6 | Pending |
| CONT-01 | Phase 7 | Pending |
| CONT-02 | Phase 7 | Pending |
| CONT-03 | Phase 7 | Pending |
| DIST-ET-01–07 | Phase 9 | Pending |
| ECOM-01–08 | Phase 10 | Pending |
| SYMP-01–10 | Phase 11 | Pending |
| ACAD-01–10 | Phase 12 | Pending |
| TUTOR-01–08 | Phase 13 | Pending |
| TWIN-01–08 | Phase 14 | Pending |
| DASH-01–06 | Phase 15 | Pending |

**Coverage:**
- v1 requirements (Phases 1–8): 33 total, 33 mapped
- Master Document requirements (Phases 9–15): 57 total, 57 mapped
- **Grand total: 90 requirements, 90 mapped, 0 unmapped** ✓

---
*Requirements defined: 2026-03-17*
*Last updated: 2026-03-20 — Added 57 requirements for Phases 9–15 (Master Document gap closure)*
