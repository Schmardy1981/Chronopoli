# Chronopoli – Deployment Handbook

**For: DevOps Engineer**
**Platform: OpenEdX (Tutor) on AWS**
**Region: me-central-1 (UAE) — fallback: eu-west-1**
**Last updated: 2026-03-17**

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
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Route53     │────▶│  CloudFront  │────▶│  EC2 t3.xlarge  │
│  DNS         │     │  CDN + SSL   │     │  Ubuntu 22.04   │
└─────────────┘     └──────────────┘     │                 │
                                          │  Tutor/Docker:  │
                                          │  ├── LMS        │
                                          │  ├── CMS        │
                                          │  ├── Celery     │
                                          │  ├── Caddy      │
                                          │  └── Redis      │
                                          └────────┬────────┘
                                                   │
                    ┌──────────────┐                │
                    │  RDS MySQL   │◀───────────────┤
                    │  Multi-AZ    │                │
                    └──────────────┘                │
                                                   │
                    ┌──────────────┐                │
                    │  S3 Buckets  │◀───────────────┘
                    │  media/      │
                    │  static/     │
                    │  backups/    │
                    └──────────────┘
```

### Multi-Tenant Architecture

Chronopoli uses **6 Knowledge Districts**, each mapped to a separate OpenEdX Organization:

| District | Org Code | Audience |
|----------|----------|----------|
| AI District | CHRON-AI | CIOs, enterprise leaders |
| Digital Assets | CHRON-DA | Bankers, founders |
| Governance | CHRON-GOV | Policymakers, ministers |
| Compliance | CHRON-COMP | MLROs, compliance officers |
| Investigation | CHRON-INV | Law enforcement, FIUs |
| Risk & Trust | CHRON-RISK | CROs, risk managers |

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

**This creates:** EC2 + EBS, RDS MySQL, 3 S3 buckets, CloudFront CDN, Route53 DNS, ACM SSL cert, SES email, IAM roles.

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
- 6 Knowledge Districts (OpenEdX Organizations)
- 6 demo courses (one per district)
- Runs Chronopoli app migrations
- Applies the Chronopoli theme

**Duration:** ~2 minutes

---

## Step 6: Smoke Test

```bash
bash scripts/healthcheck.sh
```

This checks:
- All Docker containers running
- LMS and Studio responding (HTTP 200)
- API endpoints alive
- SSL certificate valid
- All 6 districts exist
- Database connectivity
- Disk and memory usage

**Expected result:** All checks PASS.

---

## Step 7: Verify Manually

Open in your browser:

| URL | What to check |
|-----|--------------|
| `https://learn.chronopoli.io` | LMS homepage loads |
| `https://learn.chronopoli.io/admin` | Django admin (login with admin credentials) |
| `https://studio.chronopoli.io` | Studio loads |
| `https://learn.chronopoli.io/admin/organizations/organization/` | All 6 districts visible |
| `https://learn.chronopoli.io/courses` | Demo courses visible |

### Verify Multi-Tenant Isolation

In Django Admin (`/admin`):
1. Go to **Organizations > Organizations** — verify 6 districts exist
2. Go to **Organization Courses** — verify each demo course is linked to its district
3. Create a test user, go through the onboarding flow at `/chronopoli/onboarding/start/`

---

## Step 8: SES Email Verification

AWS SES starts in sandbox mode. You need to:

1. **Verify sender email** in AWS Console → SES → Verified Identities
2. **Request production access** via AWS Support (takes 24-48h)
3. Test email: In Django Admin, trigger a password reset for your admin account

Until production access is granted, you can only send to verified email addresses.

---

## Step 9: Backups

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

## Step 10: Monitoring

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
| `infrastructure/terraform/` | All AWS resources as IaC |
| `infrastructure/production.env.template` | Environment variable template |
| `tutor/config.yml` | Tutor base config (reference only) |
| `tutor/plugins/chronopoli/` | Custom Tutor plugin |

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

*Generated: 2026-03-17*
*Platform: Chronopoli — The Global Knowledge City*
