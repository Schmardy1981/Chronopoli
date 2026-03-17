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

## v2 Requirements

Deferred to future milestones. Tracked but not in current roadmap.

### Auto-Scaling

- **SCALE-01**: Platform runs on EKS with HPA for LMS/CMS/workers
- **SCALE-02**: Auto-scales from 2-10 LMS pods based on CPU/memory
- **SCALE-03**: Helm chart packages full Chronopoli deployment

### Certificates

- **CERT-01**: Accredible integration issues certificates on course completion
- **CERT-02**: Certificates shareable to LinkedIn and email

### Community

- **COMM-01**: Circle platform integrated at community.chronopoli.io
- **COMM-02**: SSO between OpenEdX and Circle

### Analytics

- **ANLY-01**: Segment/Mixpanel tracks key user events
- **ANLY-02**: Dashboard shows enrollment, completion, district distribution

## Out of Scope

| Feature | Reason |
|---------|--------|
| openedx-platform fork | Plugin system handles all customization |
| Kubernetes/EKS | Deferred to v2 after traffic justifies cost |
| Mobile native app | Responsive web + REST API sufficient |
| Real-time chat | Circle handles community discussion |
| Video hosting | S3/CloudFront + YouTube/Vimeo embeds |
| Multi-language | English-only for professional audience |
| Payment/e-commerce | Free launch, monetization in v2 |
| OAuth/SSO login | Email/password sufficient for v1 |

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

**Coverage:**
- v1 requirements: 33 total
- Mapped to phases: 33
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-17*
*Last updated: 2026-03-17 after consolidation session*
