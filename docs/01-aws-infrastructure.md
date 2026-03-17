# 01 – AWS Infrastructure Setup

## Overview

Chronopoli runs on AWS with the following architecture:

```
Internet → Route53 → CloudFront → ALB → EC2 (OpenEdX/Tutor)
                                    └──→ RDS PostgreSQL
                                    └──→ ElastiCache Redis
                                    └──→ S3 (Media/Assets)
```

---

## 1. AWS Region

**Recommended: `me-central-1` (UAE – Abu Dhabi)** for Dubai proximity and data residency.

Alternative: `eu-west-1` (Ireland) for lower latency to European partners.

---

## 2. EC2 Instance

### Production (Phase 1)
| Parameter        | Value                    |
|------------------|--------------------------|
| Instance Type    | `t3.xlarge` (4 vCPU, 16GB RAM) |
| OS               | Ubuntu 22.04 LTS         |
| Root Volume      | 50 GB gp3 SSD            |
| Data Volume      | 100 GB gp3 SSD (mounted at /var) |
| Elastic IP       | Yes                      |

### Staging
| Parameter        | Value                    |
|------------------|--------------------------|
| Instance Type    | `t3.medium` (2 vCPU, 4GB RAM) |
| OS               | Ubuntu 22.04 LTS         |

### EC2 Security Group Rules
```
Inbound:
- Port 22   (SSH)    – Your IP only (admin access)
- Port 80   (HTTP)   – 0.0.0.0/0 (redirects to HTTPS)
- Port 443  (HTTPS)  – 0.0.0.0/0
- Port 8000 (Tutor)  – Internal VPC only

Outbound:
- All traffic – 0.0.0.0/0
```

---

## 3. RDS PostgreSQL

| Parameter        | Value                         |
|------------------|-------------------------------|
| Engine           | PostgreSQL 14                 |
| Instance Class   | `db.t3.medium`                |
| Storage          | 50 GB gp3, auto-scaling to 200 GB |
| Multi-AZ         | Yes (production)              |
| Backup Retention | 7 days                        |
| Encryption       | Enabled (AWS KMS)             |

**Databases to create:**
```sql
CREATE DATABASE openedx;
CREATE DATABASE xapi;    -- For learning analytics
```

---

## 4. ElastiCache Redis

| Parameter        | Value              |
|------------------|--------------------|
| Engine           | Redis 7.x          |
| Node Type        | `cache.t3.micro`   |
| Nodes            | 1 (Phase 1)        |
| Encryption       | In-transit + at-rest |

---

## 5. S3 Buckets

Create the following buckets:

```bash
# Media files (course videos, images, documents)
chronopoli-media-production

# Static assets (CSS, JS, fonts)
chronopoli-static-production

# Backups
chronopoli-backups-production

# Partner content staging
chronopoli-partner-uploads-production
```

**Bucket Policy (media – public read for course assets):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::chronopoli-media-production/*"
    }
  ]
}
```

---

## 6. CloudFront CDN

| Parameter         | Value                              |
|-------------------|------------------------------------|
| Origin            | Your EC2 Elastic IP or ALB         |
| SSL Certificate   | AWS Certificate Manager (ACM)      |
| Price Class       | All Edge Locations (global reach)  |
| Default TTL       | 86400 (24 hours)                   |
| Compress          | Yes                                |

**Custom domain:** `learn.chronopoli.io`

---

## 7. Route53 DNS

```
chronopoli.io          → Webflow (CNAME)
learn.chronopoli.io    → CloudFront distribution
api.chronopoli.io      → ALB (future API gateway)
community.chronopoli.io → Circle platform (CNAME)
```

---

## 8. IAM Setup

### Create deployment IAM user

```bash
# AWS CLI
aws iam create-user --user-name chronopoli-deployer

aws iam attach-user-policy \
  --user-name chronopoli-deployer \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess

aws iam attach-user-policy \
  --user-name chronopoli-deployer \
  --policy-arn arn:aws:iam::aws:policy/AmazonRDSFullAccess

aws iam attach-user-policy \
  --user-name chronopoli-deployer \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```

### EC2 Instance Role (for S3 access from server)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::chronopoli-media-production",
        "arn:aws:s3:::chronopoli-media-production/*",
        "arn:aws:s3:::chronopoli-static-production",
        "arn:aws:s3:::chronopoli-static-production/*"
      ]
    }
  ]
}
```

---

## 9. SSL Certificate

```bash
# Request certificate via ACM
aws acm request-certificate \
  --domain-name chronopoli.io \
  --subject-alternative-names "*.chronopoli.io" \
  --validation-method DNS \
  --region me-central-1
```

---

## 10. Estimated AWS Monthly Cost (Phase 1)

| Service              | Spec                    | Monthly Cost |
|----------------------|-------------------------|--------------|
| EC2 t3.xlarge        | On-Demand               | ~$150        |
| RDS db.t3.medium     | Multi-AZ                | ~$120        |
| ElastiCache t3.micro | Single node             | ~$25         |
| S3                   | 100 GB storage + requests | ~$15       |
| CloudFront           | 1 TB transfer           | ~$85         |
| Route53              | Hosted zone + queries   | ~$5          |
| Data Transfer        | Outbound                | ~$30         |
| **Total**            |                         | **~$430/mo** |

> Annual: ~$5,160. Scale to t3.2xlarge when >500 concurrent users.

---

## Next Step

→ [02-tutor-installation.md](02-tutor-installation.md)
