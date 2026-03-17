# 04 – Chronopoli Districts Configuration

## Overview

The 6 Chronopoli Knowledge Districts map to OpenEdX **Organizations** and **Course Categories**.
Each district has its own branding, course catalog, and partner tracks.

```
Chronopoli Platform
├── AI District                    (org: CHRON-AI)
├── Digital Assets District        (org: CHRON-DA)
├── Governance District            (org: CHRON-GOV)
├── Compliance District            (org: CHRON-COMP)
├── Investigation District         (org: CHRON-INV)
└── Risk & Trust District          (org: CHRON-RISK)
```

---

## District Definitions

### District 1 – AI District (`CHRON-AI`)

| Field         | Value                                              |
|---------------|----------------------------------------------------|
| Short name    | AI                                                 |
| Full name     | Chronopoli AI District                             |
| Org code      | CHRON-AI                                           |
| Color         | `#6C63FF` (purple)                                 |
| Icon          | Brain / Neural network                             |
| Audience      | Enterprise leaders, developers, risk officers      |

**Course tracks:**
- AI Governance & Responsible Deployment
- AI in Financial Crime Detection
- Enterprise AI Adoption Frameworks
- AI Risk Management
- AI in Investigations and Compliance Analytics
- Model Governance for Financial Institutions

**Partner tracks:**
- Microsoft AI – Enterprise AI Adoption Track
- Google AI – AI Infrastructure Track
- OpenAI practitioners – Applied LLM in Compliance

---

### District 2 – Digital Assets District (`CHRON-DA`)

| Field         | Value                                              |
|---------------|----------------------------------------------------|
| Short name    | Digital Assets                                     |
| Full name     | Chronopoli Digital Assets District                 |
| Org code      | CHRON-DA                                           |
| Color         | `#F59E0B` (gold)                                   |
| Icon          | Blockchain chain links                             |
| Audience      | Bankers, founders, regulators, investors           |

**Course tracks:**
- Blockchain Infrastructure for Decision Makers
- RWA Tokenization and the Future Digital Economy
- Stablecoins, Payments, and Institutional Adoption
- Digital Asset Custody and Security
- Smart Contracts in Financial Services
- DeFi for Enterprise

**Partner tracks:**
- Ripple – Digital Payments Infrastructure Track
- Cardano – Blockchain Governance Track
- Tether – Stablecoin Infrastructure Track
- Polygon – Scalable Blockchain Infrastructure
- Chainlink – Oracle Infrastructure
- Hedera – Enterprise DLT Track

---

### District 3 – Governance District (`CHRON-GOV`)

| Field         | Value                                              |
|---------------|----------------------------------------------------|
| Short name    | Governance                                         |
| Full name     | Chronopoli Governance District                     |
| Org code      | CHRON-GOV                                          |
| Color         | `#10B981` (green)                                  |
| Icon          | Scales / Institution                               |
| Audience      | Regulators, policymakers, ministers, diplomats     |

**Course tracks:**
- Digital Asset Regulation: Global Landscape
- Sovereign Digital Strategy for Governments
- Public-Private Dialogue Frameworks
- Technology Governance Design
- Regulatory Sandbox Design
- CBDC Policy and Implementation

---

### District 4 – Compliance District (`CHRON-COMP`)

| Field         | Value                                              |
|---------------|----------------------------------------------------|
| Short name    | Compliance                                         |
| Full name     | Chronopoli Compliance District                     |
| Org code      | CHRON-COMP                                         |
| Color         | `#3B82F6` (blue)                                   |
| Icon          | Shield / Checklist                                 |
| Audience      | Compliance officers, MLROs, legal teams, banks     |

**Course tracks:**
- Digital Asset Compliance and Global Regulation
- AML in Crypto: Typologies and Controls
- Travel Rule: Implementation Playbook
- Exchange Controls and Compliance
- Internal Compliance Design for Digital Institutions
- Sanctions Screening in Digital Asset Markets

---

### District 5 – Investigation District (`CHRON-INV`)

| Field         | Value                                              |
|---------------|----------------------------------------------------|
| Short name    | Investigation                                      |
| Full name     | Chronopoli Investigation District                  |
| Org code      | CHRON-INV                                          |
| Color         | `#EF4444` (red)                                    |
| Icon          | Magnifying glass / Forensics                       |
| Audience      | Law enforcement, FIUs, forensic analysts           |

**Course tracks:**
- Blockchain Forensics: Foundations
- On-Chain Investigation Techniques
- Financial Crime Typology Library
- Evidence Collection in Digital Asset Cases
- Tracing Illicit Funds: Practical Methods
- Case-Based Investigation Workshops

**Partner tracks:**
- Chainalysis – Blockchain Investigation Track
- TRM Labs – Risk Intelligence Track
- Elliptic – Forensics Tooling Track

---

### District 6 – Risk & Trust District (`CHRON-RISK`)

| Field         | Value                                              |
|---------------|----------------------------------------------------|
| Short name    | Risk & Trust                                       |
| Full name     | Chronopoli Risk & Trust District                   |
| Org code      | CHRON-RISK                                         |
| Color         | `#8B5CF6` (violet)                                 |
| Icon          | Shield + check                                     |
| Audience      | Risk managers, CROs, enterprise leaders            |

**Course tracks:**
- Operational Risk in Digital Infrastructure
- Cyber Risk in Digital Asset Systems
- Governance Failure Case Studies
- Enterprise Risk Frameworks for Digital
- Third-Party Risk in Fintech Ecosystems
- Trust Architecture for Digital Institutions

---

## Setting Up Districts in OpenEdX

### Step 1: Create Organizations

```bash
# Via Django management command
tutor local do exec lms ./manage.py lms shell

# In Django shell:
from organizations.models import Organization

districts = [
    {"name": "Chronopoli AI District", "short_name": "CHRON-AI", "description": "AI governance, model risk, enterprise AI adoption"},
    {"name": "Chronopoli Digital Assets District", "short_name": "CHRON-DA", "description": "Blockchain, tokenization, stablecoins, digital payments"},
    {"name": "Chronopoli Governance District", "short_name": "CHRON-GOV", "description": "Policy, regulation, sovereign digital strategy"},
    {"name": "Chronopoli Compliance District", "short_name": "CHRON-COMP", "description": "AML, KYC, sanctions, travel rule, compliance design"},
    {"name": "Chronopoli Investigation District", "short_name": "CHRON-INV", "description": "Blockchain forensics, financial crime, tracing"},
    {"name": "Chronopoli Risk & Trust District", "short_name": "CHRON-RISK", "description": "Operational risk, cyber risk, enterprise trust frameworks"},
]

for d in districts:
    org, created = Organization.objects.get_or_create(
        short_name=d["short_name"],
        defaults={"name": d["name"], "description": d["description"]}
    )
    print(f"{'Created' if created else 'Exists'}: {org.short_name}")
```

### Step 2: Create District Admin Users

```bash
# Create district coordinator for each district
tutor local do createuser --staff --password SecurePass123! ai-admin ai@chronopoli.io
tutor local do createuser --staff --password SecurePass123! da-admin digitalassets@chronopoli.io
tutor local do createuser --staff --password SecurePass123! gov-admin governance@chronopoli.io
tutor local do createuser --staff --password SecurePass123! comp-admin compliance@chronopoli.io
tutor local do createuser --staff --password SecurePass123! inv-admin investigation@chronopoli.io
tutor local do createuser --staff --password SecurePass123! risk-admin risk@chronopoli.io
```

### Step 3: Create First Course in Studio

Navigate to `https://studio.chronopoli.io`:

1. Click **"New Course"**
2. Course Name: `Understanding AI and Digital Assets`
3. Organization: `CHRON-AI`
4. Course Number: `AI-001`
5. Course Run: `2025-Q1`
6. → Course key: `course-v1:CHRON-AI+AI-001+2025-Q1`

---

## The 4 Learning Layers as Course Tags

Each course gets tagged with its layer:

| Tag               | Description                    |
|-------------------|--------------------------------|
| `layer:entry`     | L1 – Open awareness            |
| `layer:professional` | L2 – Role-based learning    |
| `layer:institutional` | L3 – Governments/enterprise |
| `layer:influence` | L4 – Thought leadership        |

---

## Partner Track Course Naming Convention

```
course-v1:{PARTNER_CODE}+{DISTRICT_CODE}-{NUMBER}+{YEAR}-{QUARTER}

Examples:
course-v1:RIPPLE+DA-001+2025-Q2       → Ripple Digital Payments Track
course-v1:CHAINALYSIS+INV-001+2025-Q2 → Chainalysis Investigation Track
course-v1:MICROSOFT+AI-001+2025-Q2    → Microsoft AI Enterprise Track
```

---

## Next Step

→ [05-partner-onboarding.md](05-partner-onboarding.md)
