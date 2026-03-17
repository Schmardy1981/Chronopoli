# Phase 1: AWS Infrastructure - Context

**Gathered:** 2026-03-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Provision all AWS resources for Phase 1 EC2 deployment via Terraform: EC2 instance, RDS MySQL, S3 buckets, CloudFront CDN, Route53 DNS, IAM roles, and security groups. Terraform code exists — this phase validates it and prepares for `terraform apply`.

</domain>

<decisions>
## Implementation Decisions

### AWS Region
- Primary: me-central-1 (UAE) for Dubai data residency
- Fallback: eu-west-1 (Ireland) if me-central-1 unavailable
- All resources in single region except ACM cert (us-east-1 for CloudFront)

### EC2 Configuration
- t3.xlarge (4 vCPU, 16GB RAM) — handles OpenEdX with Docker
- Ubuntu 22.04 LTS — Tutor's recommended OS
- gp3 volumes: 50GB root + 100GB data
- Elastic IP for stable DNS

### RDS Configuration
- MySQL 8.0 (OpenEdX default, not PostgreSQL)
- db.t3.medium, Multi-AZ for production
- Auto-scaling storage: 50GB initial, up to 200GB
- 7-day backup retention

### S3 Strategy
- 3 buckets: media (public read), static (public read), backups (private encrypted)
- Backup bucket has lifecycle: Glacier after 30 days, expire after 365 days
- Media bucket has versioning enabled

### Security
- SSH restricted to admin CIDR (not 0.0.0.0/0)
- RDS only accessible from EC2 security group (no public access)
- All storage encrypted (EBS, RDS, S3)
- IAM role for EC2 S3 access (no hardcoded keys)

### Claude's Discretion
- Exact Terraform module structure (flat vs nested)
- CloudFront cache behavior tuning
- Tagging conventions beyond required tags

</decisions>

<specifics>
## Specific Ideas

No specific requirements — standard AWS best practices apply. Follow the architecture documented in docs/01-aws-infrastructure.md.

</specifics>

<canonical_refs>
## Canonical References

### Infrastructure specs
- `docs/01-aws-infrastructure.md` — Complete AWS architecture, costs, IAM policies, security groups
- `docs/06-phase1-launch-checklist.md` §Phase 1 — Infrastructure provisioning checklist

### Terraform code
- `infrastructure/terraform/main.tf` — EC2, security groups, IAM, EBS
- `infrastructure/terraform/rds.tf` — RDS MySQL with Multi-AZ
- `infrastructure/terraform/s3.tf` — S3 buckets with policies and lifecycle
- `infrastructure/terraform/cloudfront.tf` — CDN and ACM certificate
- `infrastructure/terraform/variables.tf` — All input variables
- `infrastructure/terraform/outputs.tf` — Resource outputs
- `infrastructure/terraform/production.tfvars.example` — Example variable values

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Terraform files already written (7 files, complete IaC)
- deploy.sh references Tutor config deployment

### Established Patterns
- Default VPC used for Phase 1 simplicity
- All resources tagged with Project/ManagedBy/Organization
- Secrets never committed — .tfvars in .gitignore

### Integration Points
- EC2 user_data installs Docker + Tutor (feeds into Phase 2)
- RDS endpoint used in tutor/config.yml
- S3 bucket names used in tutor/config.yml
- CloudFront domain used for Route53 CNAME

</code_context>

<deferred>
## Deferred Ideas

- EKS/Kubernetes cluster — Phase 2 (Milestone 5)
- WAF (Web Application Firewall) — future security hardening
- ElastiCache Redis — using Tutor's built-in Redis for Phase 1

</deferred>

---

*Phase: 01-aws-infrastructure*
*Context gathered: 2026-03-17*
