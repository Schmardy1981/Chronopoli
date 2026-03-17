# 06 – Phase 1 Launch Checklist

## STATUS TRACKER
Use this to track deployment progress. Update as tasks are completed.

---

## PHASE 0 – Repository & AWS Setup

### GitHub
- [ ] Create GitHub organization: `chronopoli-platform` (or `dbcc-chronopoli`)
- [ ] Push this repository to GitHub
- [ ] Add team members as collaborators
- [ ] Create `main` (production) and `develop` (staging) branches
- [ ] Add GitHub Secrets:
  - [ ] `AWS_ACCESS_KEY_ID`
  - [ ] `AWS_SECRET_ACCESS_KEY`
  - [ ] `EC2_HOST` (Elastic IP)
  - [ ] `EC2_SSH_PRIVATE_KEY` (private key content)
  - [ ] `LMS_HOST` (learn.chronopoli.io)
  - [ ] `CMS_HOST` (studio.chronopoli.io)

### AWS Account
- [ ] Create AWS account or use existing DBCC account
- [ ] Configure region: `me-central-1` (UAE) or `eu-west-1`
- [ ] Create IAM user `chronopoli-deployer` with required policies
- [ ] Store AWS credentials securely (1Password / AWS Secrets Manager)

---

## PHASE 1 – Infrastructure (AWS)

### EC2
- [ ] Launch EC2 t3.xlarge (Ubuntu 22.04 LTS)
- [ ] Allocate and associate Elastic IP
- [ ] Configure Security Group (ports 22, 80, 443)
- [ ] Attach EC2 IAM role for S3 access
- [ ] Mount 100 GB data volume at `/var`
- [ ] SSH access verified ✓

### Database
- [ ] Launch RDS MySQL 8.0 (db.t3.medium, Multi-AZ)
- [ ] Create database `openedx`
- [ ] Note connection endpoint for Tutor config

### Storage
- [ ] Create S3 bucket `chronopoli-media-production`
- [ ] Create S3 bucket `chronopoli-static-production`
- [ ] Create S3 bucket `chronopoli-backups-production`
- [ ] Configure bucket policies (public read for media)

### CDN & DNS
- [ ] Request SSL certificate in ACM (wildcard: `*.chronopoli.io`)
- [ ] Create CloudFront distribution
- [ ] Configure Route53:
  - [ ] `learn.chronopoli.io` → CloudFront
  - [ ] `studio.chronopoli.io` → CloudFront
  - [ ] `community.chronopoli.io` → Circle (later)

---

## PHASE 2 – OpenEdX Installation

### Server Setup
- [ ] SSH into EC2 instance
- [ ] Clone GitHub repository: `git clone https://github.com/YOUR_ORG/chronopoli`
- [ ] Install Docker (see `docs/02-tutor-installation.md`)
- [ ] Install Tutor: `pip install tutor[full]`

### Tutor Configuration
- [ ] Copy `tutor/config.yml` to `~/.local/share/tutor/config.yml`
- [ ] Update `LMS_HOST`, `CMS_HOST`, `CONTACT_EMAIL`
- [ ] Configure RDS connection (disable `RUN_MYSQL`)
- [ ] Configure ElastiCache (disable `RUN_REDIS`)
- [ ] Configure AWS SES for email

### First Deployment
- [ ] Run: `chmod +x scripts/deploy.sh && ./scripts/deploy.sh production`
- [ ] Verify all containers running: `docker ps`
- [ ] LMS loads at `https://learn.chronopoli.io`
- [ ] Studio loads at `https://studio.chronopoli.io`
- [ ] SSL certificate valid (green padlock)

---

## PHASE 3 – Platform Configuration

### Admin Setup
- [ ] Create superuser admin account
- [ ] Log in to LMS admin at `/admin`
- [ ] Log in to Studio
- [ ] Set platform name to "Chronopoli"
- [ ] Upload platform logo

### Districts Setup (OpenEdX Organizations)
- [ ] Run district setup script (see `docs/04-districts-configuration.md`)
- [ ] Create organizations: CHRON-AI, CHRON-DA, CHRON-GOV, CHRON-COMP, CHRON-INV, CHRON-RISK
- [ ] Create district admin users

### Theme
- [ ] Deploy Chronopoli theme
- [ ] Enable theme: `tutor local do settheme chronopoli-theme`
- [ ] Verify visual look on homepage
- [ ] Test on mobile

---

## PHASE 4 – Content Setup

### Foundation Courses (Priority for Phase 1 Launch)
- [ ] Course 1: `Understanding AI and Digital Assets` (CHRON-AI)
- [ ] Course 2: `Digital Assets and Blockchain Infrastructure for Decision Makers` (CHRON-DA)
- [ ] Course 3: `Digital Asset Compliance and Global Regulation` (CHRON-COMP)
- [ ] Course 4: `Blockchain Investigations: Foundations` (CHRON-INV)

### Partner Tracks (after first 2 partner agreements signed)
- [ ] Create partner organization in OpenEdX
- [ ] Create partner track course
- [ ] Partner reviews content in Studio
- [ ] Launch partner track

---

## PHASE 5 – Community & Credentials

### Circle Community
- [ ] Sign up for Circle platform account
- [ ] Create Chronopoli community
- [ ] Configure spaces per district
- [ ] Connect Circle to OpenEdX (SSO or manual)
- [ ] Add `community.chronopoli.io` CNAME

### Accredible Certificates
- [ ] Create Accredible account
- [ ] Design Chronopoli certificate template
- [ ] Connect to OpenEdX via API key
- [ ] Test certificate issuance

---

## PHASE 6 – Go-Live

### Final Checks
- [ ] All smoke tests passed (see `docs/02-tutor-installation.md`)
- [ ] Email delivery tested (registration, password reset)
- [ ] Registration flow tested (full user journey)
- [ ] AI onboarding questionnaire working
- [ ] First course visible and accessible
- [ ] Certificate issued on course completion
- [ ] Mobile responsive verified
- [ ] Performance: page load < 3 seconds

### Launch
- [ ] Webflow marketing site live at `chronopoli.io`
- [ ] Link from Webflow to OpenEdX (`learn.chronopoli.io`)
- [ ] Announce to first partner cohort
- [ ] Soft launch event / DBCC announcement

---

## ESTIMATED TIMELINE

| Week | Milestone                           |
|------|-------------------------------------|
| 1    | AWS infra + GitHub setup            |
| 2    | OpenEdX installed + configured      |
| 3    | Theme + districts deployed          |
| 4    | First course content in Studio      |
| 5    | Community + certificates configured |
| 6    | Soft launch ✓                       |

---

## CONTACTS & RESOURCES

| Role              | Contact               |
|-------------------|-----------------------|
| Platform Admin    | admin@chronopoli.io   |
| Partner Enquiries | partners@chronopoli.io|
| Tech Support      | platform@chronopoli.io|

| Resource         | URL                                              |
|------------------|--------------------------------------------------|
| Tutor Docs       | https://docs.tutor.edly.io                       |
| OpenEdX Docs     | https://docs.openedx.org                         |
| Circle Docs      | https://help.circle.so                           |
| Accredible Docs  | https://help.accredible.com                      |
| AWS Docs         | https://docs.aws.amazon.com                      |
