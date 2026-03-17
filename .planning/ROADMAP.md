# Roadmap: Chronopoli

## Overview

Chronopoli launches in 7 phases: provision AWS infrastructure, install OpenEdX via Tutor with our plugin, configure the 6 Knowledge Districts, apply the dark/gold theme, wire up the AI onboarding questionnaire, integrate the partner ecosystem, and create the first foundation course. Each phase builds on the previous and delivers testable functionality.

## Phases

- [x] **Phase 1: AWS Infrastructure** - Provision EC2, RDS, S3, CloudFront via Terraform
- [ ] **Phase 2: OpenEdX Installation** - Tutor install with Chronopoli plugin on EC2
- [ ] **Phase 3: Districts Setup** - Create 6 Knowledge Districts as OpenEdX organizations
- [ ] **Phase 4: Theme Deployment** - Apply Chronopoli dark/gold theme with HTML templates
- [ ] **Phase 5: AI Onboarding** - Wire onboarding questionnaire into registration flow
- [ ] **Phase 6: Partner Ecosystem** - Integrate partner app and create first partner org
- [ ] **Phase 7: First Course** - Create and publish foundation course in Studio

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
| 2. OpenEdX Installation | 0/3 | Not started | - |
| 3. Districts Setup | 0/1 | Not started | - |
| 4. Theme Deployment | 0/2 | Not started | - |
| 5. AI Onboarding | 0/2 | Not started | - |
| 6. Partner Ecosystem | 0/2 | Not started | - |
| 7. First Course | 0/1 | Not started | - |
