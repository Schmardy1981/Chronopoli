# CHRONOPOLI – Global Knowledge City Platform

> Dubai Blockchain Center | OpenEdX on AWS | Phase 1 Infrastructure

Chronopoli is a global knowledge platform for AI, blockchain, governance, compliance, financial crime investigation, and enterprise risk. Hosted by the Dubai Blockchain Center (DBCC), it is built as an umbrella architecture – not a narrow course catalog.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    chronopoli.io (Webflow)                   │
│                    Public Marketing Layer                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│               OpenEdX (Tutor) – Core LMS                     │
│               Custom Chronopoli Theme (MFE)                  │
│                                                              │
│  ┌─────────┐  ┌──────────┐  ┌───────────┐  ┌────────────┐  │
│  │  AI     │  │ Digital  │  │Governance │  │ Compliance │  │
│  │District │  │ Assets   │  │ District  │  │ District   │  │
│  └─────────┘  └──────────┘  └───────────┘  └────────────┘  │
│  ┌────────────────────┐  ┌──────────────────────────────┐   │
│  │ Investigation      │  │ Risk & Trust District        │   │
│  │ District           │  │                              │   │
│  └────────────────────┘  └──────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
         │                    │                    │
┌────────▼───────┐  ┌─────────▼──────┐  ┌─────────▼──────┐
│  AI Onboarding │  │  Circle / Forum │  │  Accredible    │
│  (Custom MFE)  │  │  Community Hub  │  │  Certificates  │
└────────────────┘  └────────────────┘  └────────────────┘
         │
┌────────▼───────────────────────────────────────────────────┐
│              AWS Infrastructure                             │
│  EC2 (t3.xlarge) | RDS PostgreSQL | ElastiCache Redis      │
│  S3 (media/assets) | CloudFront CDN | Route53 DNS          │
└────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Component              | Technology             | Cost/year     |
|------------------------|------------------------|---------------|
| LMS Core               | OpenEdX (Tutor)        | Open Source   |
| Frontend               | OpenEdX MFE + Custom   | Open Source   |
| AI Onboarding          | Custom OpenEdX Plugin  | Dev cost only |
| Community              | Circle Platform        | ~$2,000       |
| Video Delivery         | Vimeo / Wistia         | ~$3,000       |
| Credentials            | Accredible             | ~$2,000       |
| Infrastructure         | AWS EC2 + RDS + S3     | ~$6,000–9,000 |
| Domain / CDN           | Route53 + CloudFront   | ~$500         |
| **Total Phase 1**      |                        | **~$15,000–18,000** |

> Saving $20,000+/year vs. Canvas LMS Enterprise by using OpenEdX.

---

## The 6 Knowledge Districts

| District               | Focus                                          |
|------------------------|------------------------------------------------|
| AI District            | AI governance, model risk, enterprise AI       |
| Digital Assets         | Blockchain, tokenization, stablecoins          |
| Governance District    | Policy, regulation, public-private dialogue    |
| Compliance District    | AML, KYC, sanctions, travel rule               |
| Investigation District | Blockchain forensics, financial crime          |
| Risk & Trust           | Operational risk, cyber risk, governance       |

---

## The 4 Learning Layers

| Layer | Name                | Audience                                  |
|-------|---------------------|-------------------------------------------|
| L1    | Entry Layer         | Students, newcomers, public               |
| L2    | Professional Layer  | Executives, compliance teams, founders    |
| L3    | Institutional Layer | Governments, regulators, enterprise       |
| L4    | Influence Layer     | Thought leaders, policy shapers           |

---

## Partner Ecosystem

Partners participate as **Chronopoli Knowledge Partners** and host district-branded tracks.

| Tier                      | Examples                           |
|---------------------------|------------------------------------|
| Founding Knowledge        | Ripple, Cardano, Hedera            |
| Strategic Knowledge       | Tether, Polygon, Chainlink         |
| Compliance & Investigation| Chainalysis, TRM Labs, Elliptic    |
| AI Ecosystem              | Microsoft AI, Google AI            |
| Institutional             | Universities, think tanks, banks   |

---

## Repository Structure

```
chronopoli/
├── README.md                          # This file
├── docs/
│   ├── 01-aws-infrastructure.md       # AWS setup guide
│   ├── 02-tutor-installation.md       # OpenEdX via Tutor
│   ├── 03-custom-theme.md             # Chronopoli theme guide
│   ├── 04-districts-configuration.md  # Setting up districts
│   ├── 05-partner-onboarding.md       # Partner setup workflow
│   └── 06-phase1-launch-checklist.md  # Launch checklist
├── infrastructure/
│   ├── terraform/                     # AWS IaC with Terraform
│   └── cloudformation/                # Alternative CFN templates
├── tutor/
│   ├── config.yml                     # Tutor base configuration
│   └── plugins/
│       └── chronopoli/                # Custom Tutor plugin
├── theme/
│   └── chronopoli-theme/              # Custom OpenEdX theme
│       ├── lms/
│       └── cms/
├── plugins/
│   ├── ai-onboarding/                 # AI onboarding MFE plugin
│   ├── partner-ecosystem/             # Partner management
│   └── district-taxonomy/             # District structure plugin
├── scripts/
│   ├── deploy.sh                      # Deployment automation
│   ├── backup.sh                      # Database backup
│   └── update.sh                      # Platform updates
└── .github/
    └── workflows/
        ├── deploy-production.yml       # CI/CD production
        └── deploy-staging.yml         # CI/CD staging
```

---

## Quick Start

### Prerequisites
- AWS Account with IAM permissions
- Domain name (e.g., chronopoli.io)
- Ubuntu 22.04 LTS server (t3.xlarge minimum)
- GitHub account

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_ORG/chronopoli.git
cd chronopoli
```

### 2. Setup AWS Infrastructure
```bash
cd infrastructure/terraform
terraform init
terraform plan -var-file="production.tfvars"
terraform apply
```

### 3. Install OpenEdX
```bash
cd ../../scripts
./deploy.sh --environment production
```

Full setup guide: [docs/01-aws-infrastructure.md](docs/01-aws-infrastructure.md)

---

## Phase 1 Launch Roadmap

| Phase | Timeframe | Goal                                        |
|-------|-----------|---------------------------------------------|
| 1     | 0–3 mo    | Platform setup, first partner conversations |
| 2     | 3–6 mo    | Website live, foundation tracks launched    |
| 3     | 6–12 mo   | Executive programs, public sector tracks    |
| 4     | 12+ mo    | Annual summit, global scaling               |

---

## License
Proprietary – Dubai Blockchain Center / Chronopoli. All rights reserved.
