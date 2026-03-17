# 02 – OpenEdX Installation via Tutor

## What is Tutor?

Tutor is the official Docker-based deployment tool for OpenEdX. It replaces the old Ansible-based setup and is the only supported production method as of OpenEdX Redwood (2024+).

**Why Tutor:**
- Docker-based: consistent, reproducible deployments
- Built-in SSL, Nginx, Celery workers
- Plugin architecture (we use this for Chronopoli customizations)
- One-command upgrades
- GitHub Actions compatible

---

## 1. Server Preparation (Ubuntu 22.04)

SSH into your AWS EC2 instance:

```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

### System update
```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y \
  git curl wget unzip \
  python3 python3-pip \
  build-essential \
  ca-certificates gnupg lsb-release
```

### Install Docker
```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) \
  signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin

sudo usermod -aG docker $USER
newgrp docker

# Verify
docker --version
docker compose version
```

---

## 2. Install Tutor

```bash
pip install "tutor[full]"

# Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify
tutor --version
```

---

## 3. Configure Tutor

```bash
# Interactive setup
tutor config save --interactive
```

When prompted, enter:

```
LMS_HOST: learn.chronopoli.io
CMS_HOST: studio.chronopoli.io
PLATFORM_NAME: Chronopoli
CONTACT_EMAIL: platform@chronopoli.io
ENABLE_HTTPS: true  (yes)
```

This creates `~/.local/share/tutor/config.yml`.

### Apply our custom config
```bash
# Copy our pre-configured settings
cp /path/to/chronopoli/tutor/config.yml ~/.local/share/tutor/config.yml
```

---

## 4. Install Chronopoli Tutor Plugin

```bash
# Install our custom plugin
pip install -e /path/to/chronopoli/tutor/plugins/chronopoli/

# Enable it
tutor plugins enable chronopoli
tutor config save
```

---

## 5. Build & Launch

```bash
# Build Docker images (takes 10–20 min first time)
tutor images build openedx

# Initialize databases (first run only)
tutor local do init

# Start all services
tutor local start -d

# Check running containers
docker ps
```

Expected containers:
```
chronopoli-lms-1         ← Main LMS
chronopoli-cms-1         ← Course Studio
chronopoli-lms-worker-1  ← Celery async tasks
chronopoli-cms-worker-1  ← CMS tasks
chronopoli-nginx-1       ← Web server + SSL
chronopoli-mysql-1       ← (if not using RDS)
chronopoli-mongodb-1     ← Course content store
chronopoli-redis-1       ← (if not using ElastiCache)
chronopoli-smtp-1        ← Email relay
```

---

## 6. Connect External AWS Services

### RDS PostgreSQL (replace internal MySQL)

Edit `~/.local/share/tutor/config.yml`:
```yaml
# Disable internal MySQL, use RDS
RUN_MYSQL: false
MYSQL_HOST: your-rds-endpoint.rds.amazonaws.com
MYSQL_PORT: 3306
MYSQL_ROOT_PASSWORD: your-secure-password
MYSQL_ROOT_USERNAME: admin
```

> Note: OpenEdX uses MySQL by default. For PostgreSQL, use the tutor-contrib-postgresql plugin.

### ElastiCache Redis
```yaml
RUN_REDIS: false
REDIS_HOST: your-elasticache-endpoint.cache.amazonaws.com
REDIS_PORT: 6379
```

### S3 for Media Storage
```yaml
OPENEDX_AWS_ACCESS_KEY: YOUR_AWS_KEY
OPENEDX_AWS_SECRET_ACCESS_KEY: YOUR_AWS_SECRET
S3_STORAGE_BUCKET: chronopoli-media-production
S3_FILE_UPLOAD_BUCKET: chronopoli-media-production
AWS_DEFAULT_REGION: me-central-1
```

---

## 7. Create Admin User

```bash
tutor local do createuser \
  --superuser \
  --staff \
  --password AdminPassword123! \
  admin admin@chronopoli.io
```

---

## 8. Apply Chronopoli Theme

```bash
# Copy theme to Tutor themes directory
cp -r /path/to/chronopoli/theme/chronopoli-theme \
  "$(tutor config printroot)/env/build/openedx/themes/"

# Enable theme
tutor local do settheme chronopoli-theme

# Rebuild with theme
tutor images build openedx
tutor local restart
```

---

## 9. Configure Email (AWS SES)

```bash
# Setup AWS SES for transactional email
aws ses verify-domain-identity --domain chronopoli.io
```

Update `config.yml`:
```yaml
SMTP_HOST: email-smtp.me-central-1.amazonaws.com
SMTP_PORT: 587
SMTP_USE_TLS: true
SMTP_USERNAME: your-ses-smtp-user
SMTP_PASSWORD: your-ses-smtp-password
DEFAULT_FROM_EMAIL: noreply@chronopoli.io
```

---

## 10. Enable Tutor Plugins

```bash
# Course completion certificates
tutor plugins enable mfe          # Micro-frontends
tutor plugins enable indigo       # Modern UI (base for our theme)
tutor plugins enable notes        # In-course notes
tutor plugins enable forum        # Discussion forums

# Our custom plugins
tutor plugins enable chronopoli
tutor plugins enable chronopoli-ai-onboarding
tutor plugins enable chronopoli-districts

tutor config save
tutor images build openedx
tutor local restart
```

---

## 11. SSL Certificate Setup

Tutor handles SSL automatically via Caddy (included):

```bash
# Ensure ports 80 and 443 are open in Security Group
# Then:
tutor local start -d

# Caddy automatically fetches Let's Encrypt certificate
# Check:
tutor local logs nginx
```

---

## 12. Smoke Test Checklist

After startup, verify:

- [ ] `https://learn.chronopoli.io` loads (LMS homepage)
- [ ] `https://studio.chronopoli.io` loads (CMS)
- [ ] Admin login works at `/admin`
- [ ] Registration flow works
- [ ] Email delivery works (check AWS SES)
- [ ] SSL certificate is valid (green padlock)
- [ ] Media uploads work (test with course image)

---

## 13. Useful Tutor Commands

```bash
# View logs
tutor local logs -f lms

# Restart specific service
tutor local restart lms

# Run Django management commands
tutor local do exec lms ./manage.py lms shell

# Database shell
tutor local do exec mysql mysql -u root -p

# Backup
tutor local do exec mysql mysqldump -u root -p openedx > backup.sql

# Update OpenEdX
tutor upgrade --from=redwood
tutor local start -d
```

---

## Next Step

→ [03-custom-theme.md](03-custom-theme.md)
