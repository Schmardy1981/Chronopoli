# Chronopoli – Deployment Handbook

**For: DevOps Engineer**
**Platform: OpenEdX (Tutor) on AWS**
**Region: me-central-1 (UAE) — fallback: eu-west-1**
**Last updated: 2026-03-20**

---

## Overview

This handbook gets you from zero to a running Chronopoli platform on AWS.
Everything is automated where possible — your job is to:

1. Run Terraform to create AWS infrastructure
2. SSH into the EC2 instance
3. Run 4 scripts in order
4. Verify with healthcheck

**Expected time: 45-60 minutes** (including Docker image build)

### Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────────────────┐
│  Route53     │────▶│  CloudFront  │────▶│  EC2 t3.xlarge           │
│  DNS         │     │  CDN + SSL   │     │  Ubuntu 22.04            │
│              │     └──────────────┘     │                          │
│ learn.       │                          │  Tutor/Docker:           │
│ studio.      │          ┌──────────────▶│  ├── LMS (:80)           │
│ community.   │──────────┤ Nginx        ││  ├── CMS                 │
│ video.       │          │ Reverse      ││  ├── Celery              │
│ slides.      │          │ Proxy        ││  ├── Caddy               │
└─────────────┘          └──────────────▶│  └── Redis               │
                                          │                          │
                                          │  Extensions:             │
                                          │  ├── Discourse (:443)    │
                                          │  ├── Opencast  (:8080)   │
                                          │  └── Presenton (:5050)   │
                                          └────────────┬─────────────┘
                                                       │
                    ┌──────────────┐                    │
                    │  RDS MySQL   │◀──────────────────┤
                    │  Multi-AZ    │                    │
                    └──────────────┘                    │
                                                       │
                    ┌──────────────┐                    │
                    │  S3 Buckets  │◀───────────────────┘
                    │  media/      │
                    │  static/     │
                    │  backups/    │
                    │  opencast/   │
                    └──────────────┘
```

### Multi-Tenant Architecture

Chronopoli uses **7 Knowledge Districts**, each mapped to a separate OpenEdX Organization:

| District | Org Code | Audience |
|----------|----------|----------|
| AI District | CHRON-AI | CIOs, enterprise leaders |
| Digital Assets | CHRON-DA | Bankers, founders |
| Governance | CHRON-GOV | Policymakers, ministers |
| Compliance | CHRON-COMP | MLROs, compliance officers |
| Investigation | CHRON-INV | Law enforcement, FIUs |
| Risk & Trust | CHRON-RISK | CROs, risk managers |
| Emerging Tech | CHRON-ET | Researchers, innovation leaders |

**Key rule:** Every course belongs to exactly one district (org). Users are routed to their district via the AI Onboarding questionnaire. Partners host courses within specific districts.

---

## Prerequisites

Before you start, ensure you have:

- [ ] AWS account with admin access
- [ ] AWS CLI configured (`aws configure`)
- [ ] Terraform >= 1.5.0 installed
- [ ] SSH key pair created in AWS Console (region: me-central-1)
- [ ] Domain `chronopoli.io` accessible (you'll update nameservers)
- [ ] This repo cloned locally

---

## Step 1: AWS Infrastructure (Terraform)

### 1.1 Configure Variables

```bash
cd infrastructure/terraform

# Copy the example and fill in your values
cp production.tfvars.example production.tfvars
```

**Edit `production.tfvars`** — the critical values:

| Variable | What to set |
|----------|-------------|
| `ec2_key_name` | Your SSH key pair name from AWS Console |
| `rds_password` | Strong password (32+ chars, mixed case, numbers, symbols) |
| `admin_ssh_cidr` | Your IP address + `/32` (e.g., `203.0.113.50/32`) |
| `aws_region` | `me-central-1` or `eu-west-1` if UAE region unavailable |

### 1.2 Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Preview what will be created (review carefully!)
terraform plan -var-file=production.tfvars

# Apply (type 'yes' when prompted)
terraform apply -var-file=production.tfvars
```

**This creates:** EC2 + EBS, RDS MySQL, 4 S3 buckets (media, static, backups, opencast), CloudFront CDN, Route53 DNS (learn/studio/community/video/slides), ACM SSL cert, SES email, IAM roles.

**Duration:** ~15 minutes (RDS takes the longest)

### 1.3 Save Outputs

```bash
# Print all outputs (you'll need these)
terraform output

# Auto-generate production.env values
terraform output -raw engineer_env_config
```

**Copy the `engineer_env_config` output** — you'll use it in Step 3.

### 1.4 Update Domain Nameservers

```bash
# Get the Route53 nameservers
terraform output route53_nameservers
```

Go to your domain registrar and update the nameservers to the 4 values shown. DNS propagation takes 15-60 minutes.

---

## Step 2: Server Setup (SSH into EC2)

### 2.1 Connect

```bash
# Get the EC2 IP
terraform output ec2_public_ip

# SSH in
ssh -i ~/.ssh/your-key.pem ubuntu@<EC2_PUBLIC_IP>
```

### 2.2 Clone the Repository

```bash
# On the EC2 instance:
sudo mkdir -p /opt/chronopoli
sudo chown ubuntu:ubuntu /opt/chronopoli
git clone https://github.com/YOUR_ORG/chronopoli.git /opt/chronopoli/repo
cd /opt/chronopoli/repo
```

### 2.3 Run Server Setup

```bash
sudo bash scripts/setup-server.sh
```

**This installs:** Docker, Tutor, configures firewall (UFW), fail2ban, mounts EBS data volume at `/data`, creates 4GB swap, tunes system limits.

**Duration:** ~5 minutes

**After this, log out and log back in** (for Docker group to take effect):

```bash
exit
ssh -i ~/.ssh/your-key.pem ubuntu@<EC2_PUBLIC_IP>
```

---

## Step 3: Configure Tutor (Wire AWS Services)

### 3.1 Create Production Environment File

```bash
# Copy template
cp /opt/chronopoli/repo/infrastructure/production.env.template /data/chronopoli/production.env

# Edit with the values from Terraform outputs (Step 1.3)
nano /data/chronopoli/production.env
```

**Fill in ALL `CHANGE_THIS` values.** The most important ones:

| Variable | Where to get it |
|----------|----------------|
| `MYSQL_HOST` | `terraform output rds_address` |
| `MYSQL_ROOT_PASSWORD` | The password you set in `production.tfvars` |
| `S3_MEDIA_BUCKET` | `terraform output s3_media_bucket` |
| `S3_STATIC_BUCKET` | `terraform output s3_static_bucket` |
| `S3_BACKUPS_BUCKET` | `terraform output s3_backups_bucket` |
| `SMTP_USERNAME` | `terraform output ses_smtp_username` |
| `SMTP_PASSWORD` | `terraform output -raw ses_smtp_password` |
| `CLOUDFRONT_DOMAIN` | `terraform output cloudfront_domain` |
| `ADMIN_PASSWORD` | Choose a strong admin password |

### 3.2 Run Configuration Script

```bash
cd /opt/chronopoli/repo
bash scripts/configure-tutor.sh --env-file /data/chronopoli/production.env
```

**This configures:** Tutor to use external RDS, S3, SES. Installs the Chronopoli Tutor plugin. Enables MFE, notes, forum plugins. Generates S3 settings for LMS.

**Duration:** ~2 minutes

---

## Step 4: Build & Launch OpenEdX

### 4.1 Build Docker Images

```bash
# This builds the OpenEdX Docker image with our customizations
tutor images build openedx
```

**Duration:** 10-20 minutes (first build downloads ~2GB)

### 4.2 Start the Platform

```bash
# Start all services in background
tutor local start -d

# Watch logs to verify startup
tutor local logs -f --tail=50
```

Wait until you see `lms` and `cms` reporting healthy. Press `Ctrl+C` to exit logs.

### 4.3 Initialize Database

```bash
# Run OpenEdX migrations and setup (first time only)
tutor local do init
```

**Duration:** ~5 minutes

---

## Step 5: District Setup (Multi-Tenant)

```bash
cd /opt/chronopoli/repo
bash scripts/setup-districts.sh --env-file /data/chronopoli/production.env
```

**This creates:**
- Admin superuser
- 7 Knowledge Districts (OpenEdX Organizations)
- 7 demo courses (one per district)
- Runs Chronopoli app migrations
- Applies the Chronopoli theme

**Duration:** ~2 minutes

---

## Step 6: Discourse Community Forum

Discourse provides the community forum at `community.chronopoli.io`, integrated via SSO with OpenEdX.

### 6.1 Configure Environment

Ensure these variables are set in `/data/chronopoli/production.env`:

| Variable | Description |
|----------|-------------|
| `DISCOURSE_HOSTNAME` | `community.chronopoli.io` |
| `DISCOURSE_SMTP_USER_NAME` | SES SMTP username (from Terraform) |
| `DISCOURSE_SMTP_PASSWORD` | SES SMTP password (from Terraform) |
| `DISCOURSE_DB_PASSWORD` | Strong database password for Discourse |
| `DISCOURSE_SSO_SECRET` | Random 64-char string (shared with OpenEdX) |
| `DISCOURSE_S3_BUCKET` | S3 bucket for uploads |

### 6.2 Install Discourse

```bash
cd /opt/chronopoli/repo
sudo bash scripts/setup-discourse.sh --env-file /data/chronopoli/production.env
```

**This does:**
- Clones `discourse_docker` to `/var/discourse`
- Generates `app.yml` config with SES email, SSO, and S3 storage
- Bootstraps the Discourse container (~10 minutes)
- Starts Discourse

**Duration:** ~15 minutes

### 6.3 Post-Install: Generate API Key

1. Open `https://community.chronopoli.io` and complete the wizard
2. Go to **Admin → API → New API Key** (Global, All Users)
3. Copy the key and update `DISCOURSE_API_KEY` in your `.env` file
4. Update the Tutor config:
   ```bash
   tutor config save --set CHRONOPOLI_DISCOURSE_API_KEY=<your-api-key>
   tutor local restart lms
   ```

### 6.4 Create District Categories & Groups

```bash
bash scripts/setup-discourse-categories.sh --env-file /data/chronopoli/production.env
```

**This creates:** 7 district groups, 7 top-level categories, 28+ sub-categories (learning layers + partner tracks).

### 6.5 Verify SSO

1. Log out of Discourse
2. Click "Log In" — should redirect to OpenEdX login
3. After authenticating, should return to Discourse as logged-in user
4. Verify the user is added to their district group (check Admin → Users)

---

## Step 7: Opencast Video Platform

Opencast provides video management at `video.chronopoli.io`, integrated via LTI into OpenEdX courses.

### 7.1 Configure Environment

Ensure these variables are set in `/data/chronopoli/production.env`:

| Variable | Description |
|----------|-------------|
| `OPENCAST_DB_PASSWORD` | Database password for Opencast |
| `OPENCAST_ADMIN_PASSWORD` | Admin UI password |
| `OPENCAST_DIGEST_PASSWORD` | Internal digest password |
| `OPENCAST_LTI_KEY` | LTI consumer key (shared with OpenEdX) |
| `OPENCAST_LTI_SECRET` | LTI consumer secret (shared with OpenEdX) |

### 7.2 Install Opencast

```bash
cd /opt/chronopoli/repo
bash scripts/setup-opencast.sh --env-file /data/chronopoli/production.env
```

**This does:**
- Creates `opencast` database on RDS
- Starts Opencast container via Docker Compose
- Waits for health check
- Configures S3 storage for recordings

**Duration:** ~5 minutes

### 7.3 Verify Opencast

```bash
curl -s -o /dev/null -w "%{http_code}" https://video.chronopoli.io/info/health
# Expected: 200
```

Open `https://video.chronopoli.io` and log in with admin credentials.

### 7.4 LTI Integration in OpenEdX

To embed Opencast videos in courses:

1. In Studio, add an **LTI Consumer** component to a course unit
2. Configure:
   - **LTI URL:** `https://video.chronopoli.io/lti`
   - **LTI Key:** Value of `OPENCAST_LTI_KEY`
   - **LTI Secret:** Value of `OPENCAST_LTI_SECRET`
3. Students will see the Opencast player inline in the course

---

## Step 8: Presenton AI Slide Builder

Presenton provides AI-powered slide generation at `slides.chronopoli.io` (staff-only).

### 8.1 Configure Environment

| Variable | Description |
|----------|-------------|
| `PRESENTON_ANTHROPIC_KEY` | Anthropic API key for Claude |
| `PRESENTON_PEXELS_KEY` | Pexels API key for stock images |
| `PRESENTON_STAFF_USER` | Basic auth username for staff access |
| `PRESENTON_STAFF_PASSWORD` | Basic auth password for staff access |

### 8.2 Install Presenton

```bash
cd /opt/chronopoli/repo
bash scripts/setup-presenton.sh --env-file /data/chronopoli/production.env
```

**This does:**
- Starts Presenton container via Docker Compose
- Creates `.htpasswd` file for Nginx basic auth
- Configures Nginx reverse proxy

**Duration:** ~2 minutes

### 8.3 Install Nginx Configs

```bash
# Copy extension proxy configs
sudo cp infrastructure/nginx/extensions.conf /etc/nginx/sites-available/chronopoli-extensions.conf
sudo ln -s /etc/nginx/sites-available/chronopoli-extensions.conf /etc/nginx/sites-enabled/

# Get SSL certificates
sudo certbot certonly --nginx -d community.chronopoli.io -d video.chronopoli.io -d slides.chronopoli.io

# Test and reload
sudo nginx -t && sudo systemctl reload nginx
```

### 8.4 Using Presenton

1. Open `https://slides.chronopoli.io` (staff credentials required)
2. Use the district-specific prompt prefixes from `docs/presenton-prompts.md`
3. Generated slides follow Chronopoli brand guidelines per district

---

## Step 9: Stripe E-Commerce Setup

Stripe enables paid courses, corporate subscriptions, and partner revenue sharing.

### 9.1 Get Stripe Keys

1. Create a Stripe account at [stripe.com](https://stripe.com)
2. Go to **Developers > API Keys** — copy:
   - Secret key (`sk_live_...`)
   - Publishable key (`pk_live_...`)
3. Go to **Developers > Webhooks > Add endpoint**:
   - URL: `https://learn.chronopoli.io/chronopoli/ecommerce/webhook/stripe/`
   - Events: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`
   - Copy the webhook signing secret (`whsec_...`)
4. For partner revenue splitting: enable **Stripe Connect** in Dashboard > Settings

### 9.2 Store Keys in AWS SSM (recommended)

```bash
# From your local machine (with AWS CLI configured):
aws ssm put-parameter --name "/chronopoli/stripe/secret_key" \
  --type SecureString --value "sk_live_YOUR_KEY" --region me-central-1

aws ssm put-parameter --name "/chronopoli/stripe/webhook_secret" \
  --type SecureString --value "whsec_YOUR_SECRET" --region me-central-1

aws ssm put-parameter --name "/chronopoli/stripe/publishable_key" \
  --type String --value "pk_live_YOUR_KEY" --region me-central-1
```

### 9.3 Configure Tutor with Stripe Keys

```bash
# On EC2:
tutor config save \
  --set STRIPE_SECRET_KEY="sk_live_YOUR_KEY" \
  --set STRIPE_PUBLISHABLE_KEY="pk_live_YOUR_KEY" \
  --set STRIPE_WEBHOOK_SECRET="whsec_YOUR_SECRET"

tutor local restart lms
```

### 9.4 Create Course Pricing

In Django Admin (`/admin/chronopoli_ecommerce/coursepricingtier/`):

1. Click **Add Course Pricing Tier**
2. Set:
   - Course Key: `course-v1:CHRON-AI+AI-101+2026`
   - Layer: L1 (Entry)
   - Price: `49.00`
   - Is Free: unchecked
   - District: `CHRON-AI`
3. Repeat for each paid course

### 9.5 Test Checkout Flow

1. Open `https://learn.chronopoli.io/chronopoli/ecommerce/checkout/course-v1:CHRON-AI+AI-101+2026/`
2. Should redirect to Stripe Checkout
3. Use test card: `4242 4242 4242 4242` (any future date, any CVC)
4. After payment: redirected back to success page + auto-enrolled in course
5. Verify in Django Admin: Purchase record shows `status=completed, enrolled=True`

### 9.6 Set Up Partner Revenue Split (Stripe Connect)

For partners like Ripple, Chainalysis etc.:

1. Partner creates a Stripe Express account via the onboarding link
2. In Django Admin (`/admin/chronopoli_partners/partner/`), add:
   - `stripe_connect_account_id`: Partner's Stripe account ID (`acct_...`)
3. When a student buys a partner course: 70% auto-transfers to partner, 30% retained

---

## Step 10: Smoke Test

```bash
bash scripts/healthcheck.sh
```

This checks:
- All Docker containers running
- LMS and Studio responding (HTTP 200)
- API endpoints alive
- SSL certificate valid
- All 7 districts exist
- Database connectivity
- Disk and memory usage
- Extension services (Discourse, Opencast, Presenton)

**Expected result:** All checks PASS.

---

## Step 11: Verify Manually

Open in your browser:

| URL | What to check |
|-----|--------------|
| `https://learn.chronopoli.io` | LMS homepage loads |
| `https://learn.chronopoli.io/admin` | Django admin (login with admin credentials) |
| `https://studio.chronopoli.io` | Studio loads |
| `https://learn.chronopoli.io/admin/organizations/organization/` | All 7 districts visible |
| `https://learn.chronopoli.io/courses` | Demo courses visible |
| `https://community.chronopoli.io` | Discourse forum loads |
| `https://video.chronopoli.io` | Opencast admin loads |
| `https://slides.chronopoli.io` | Presenton loads (staff auth required) |

### Verify Multi-Tenant Isolation

In Django Admin (`/admin`):
1. Go to **Organizations > Organizations** — verify 7 districts exist
2. Go to **Organization Courses** — verify each demo course is linked to its district
3. Create a test user, go through the onboarding flow at `/chronopoli/onboarding/start/`

---

## Step 12: SES Email Verification

AWS SES starts in sandbox mode. You need to:

1. **Verify sender email** in AWS Console → SES → Verified Identities
2. **Request production access** via AWS Support (takes 24-48h)
3. Test email: In Django Admin, trigger a password reset for your admin account

Until production access is granted, you can only send to verified email addresses.

---

## Step 13: Backups

### Automated Backup (cron)

```bash
# Add to crontab — daily at 3 AM UTC
(crontab -l 2>/dev/null; echo "0 3 * * * /opt/chronopoli/repo/scripts/backup.sh >> /var/log/chronopoli-backup.log 2>&1") | crontab -

# Full backup (including media) — weekly on Sundays
(crontab -l 2>/dev/null; echo "0 4 * * 0 /opt/chronopoli/repo/scripts/backup.sh --full >> /var/log/chronopoli-backup.log 2>&1") | crontab -
```

### Manual Backup

```bash
bash scripts/backup.sh          # Database + config only
bash scripts/backup.sh --full   # Database + config + media files
```

Backups go to `s3://chronopoli-backups-production/` with Glacier archival at 30 days.

---

## Step 14: Monitoring

### Logs

```bash
# All services
tutor local logs -f --tail=100

# Specific service
tutor local logs -f lms
tutor local logs -f cms
tutor local logs -f caddy

# Deployment log
tail -f /var/log/chronopoli-deploy.log
```

### System Health

```bash
# Resource usage
htop

# Docker status
docker stats --no-stream

# Disk usage
df -h /data

# Tutor status
tutor local status
```

### CloudWatch (recommended)

Install the CloudWatch agent for automated monitoring:

```bash
sudo apt-get install -y amazon-cloudwatch-agent
# Configure with: /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

---

## Troubleshooting

### LMS not loading

```bash
# Check if containers are running
tutor local status

# Check LMS logs for errors
tutor local logs lms --tail=200

# Restart everything
tutor local stop && tutor local start -d
```

### Database connection failed

```bash
# Test RDS connectivity from EC2
mysql -h <RDS_ENDPOINT> -u admin -p -e "SELECT 1;"

# Check security group allows EC2 → RDS
# RDS SG should allow port 3306 from EC2's security group
```

### SSL certificate not working

```bash
# Check ACM validation status
aws acm describe-certificate --certificate-arn <ARN> --region us-east-1

# DNS must be propagated — check:
dig +short learn.chronopoli.io
nslookup learn.chronopoli.io
```

### Email not sending

```bash
# Check SES sending stats
aws ses get-send-statistics --region me-central-1

# Check SES identity verification
aws ses get-identity-verification-attributes --identities chronopoli.io --region me-central-1

# Verify SMTP credentials work
tutor local do exec lms python manage.py lms shell -c "
from django.core.mail import send_mail
send_mail('Test', 'Testing Chronopoli email', 'noreply@chronopoli.io', ['your@email.com'])
print('Sent')
"
```

### Disk full

```bash
# Check what's using space
du -sh /data/*
docker system df

# Clean Docker cache
docker system prune -f
docker image prune -a -f
```

### Tutor plugin not loading

```bash
# Verify plugin is installed
tutor plugins list

# Reinstall
source /opt/chronopoli/venv/bin/activate
pip install -e /opt/chronopoli/repo/tutor/plugins/chronopoli/
tutor plugins enable chronopoli
tutor config save
```

---

## File Reference

| File | Purpose |
|------|---------|
| `scripts/setup-server.sh` | EC2 server provisioning (Docker, Tutor, firewall) |
| `scripts/configure-tutor.sh` | Wire Tutor to AWS services (RDS, S3, SES) |
| `scripts/setup-districts.sh` | Create 6 districts, admin, demo courses |
| `scripts/healthcheck.sh` | Smoke tests (run after every deployment) |
| `scripts/backup.sh` | Database + media backup to S3 |
| `scripts/deploy.sh` | Update deployment (git pull + rebuild) |
| `scripts/setup-discourse.sh` | Discourse installation + SSO config |
| `scripts/setup-discourse-categories.sh` | District groups + categories on Discourse |
| `scripts/setup-opencast.sh` | Opencast installation + RDS database |
| `scripts/setup-presenton.sh` | Presenton installation + basic auth |
| `infrastructure/terraform/` | All AWS resources as IaC |
| `infrastructure/extensions/docker-compose.yml` | Opencast + Presenton containers |
| `infrastructure/extensions/.env.template` | Extension services env template |
| `infrastructure/nginx/extensions.conf` | Nginx proxy for video + slides subdomains |
| `infrastructure/production.env.template` | Environment variable template |
| `tutor/config.yml` | Tutor base config (reference only) |
| `tutor/plugins/chronopoli/` | Custom Tutor plugin |
| `plugins/ai-onboarding/` | AI onboarding questionnaire Django app |
| `plugins/partner-ecosystem/` | Partner management Django app |
| `plugins/discourse-sso/` | Discourse SSO Django app |
| `plugins/ecommerce/` | Stripe payment integration Django app |
| `docs/presenton-prompts.md` | Per-district AI slide generation prompts |

---

## Update Procedure

When deploying code changes:

```bash
cd /opt/chronopoli/repo
git pull origin main

# Reinstall plugin if changed
source /opt/chronopoli/venv/bin/activate
pip install -e tutor/plugins/chronopoli/
tutor config save

# Rebuild and restart
tutor images build openedx
tutor local stop
tutor local start -d
tutor local do init  # only if migrations changed

# Verify
bash scripts/healthcheck.sh
```

Or use the deploy script:

```bash
bash scripts/deploy.sh production
```

---

## Security Checklist

- [ ] SSH access restricted to your IP only (`admin_ssh_cidr` in tfvars)
- [ ] RDS not publicly accessible (enforced by security group)
- [ ] All secrets in environment variables (never in git)
- [ ] HTTPS enforced via CloudFront redirect
- [ ] Fail2ban active for SSH protection
- [ ] UFW firewall: only ports 22, 80, 443 open
- [ ] Backup encryption: KMS on S3 backup bucket
- [ ] RDS encryption: storage_encrypted = true
- [ ] Regular password rotation for admin and RDS

---

## Cost Estimate (Phase 1)

| Service | Spec | Monthly Cost |
|---------|------|-------------|
| EC2 | t3.xlarge (4 vCPU, 16GB) | ~$120 |
| RDS | db.t3.medium Multi-AZ | ~$140 |
| S3 | 3 buckets (~50GB) | ~$5 |
| CloudFront | ~100GB transfer | ~$15 |
| Route53 | 1 hosted zone | ~$1 |
| SES | ~10K emails/month | ~$1 |
| EBS | 150GB gp3 | ~$15 |
| **Total** | | **~$300/month** |

---

*Generated: 2026-03-20*
*Platform: Chronopoli — The Global Knowledge City*
