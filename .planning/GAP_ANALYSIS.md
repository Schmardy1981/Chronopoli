# Chronopoli – Gap Analysis
Generated: 2026-03-17

## Summary
Compared existing repo against what a complete OpenEdX Tutor deployment needs.

---

## Component Status

| Component                | Status     | What Exists                          | What's Missing                                              | Priority |
|--------------------------|------------|--------------------------------------|-------------------------------------------------------------|----------|
| **Tutor Plugin**         | 40% done   | plugin.py with hooks/filters         | pyproject.toml, __init__.py, __about__.py, patches/, templates/, proper package structure (tutorchronopoli/) | HIGH |
| **Theme**                | 40% done   | CSS file (chronopoli-main.css)       | HTML templates (header, footer, homepage), JS interactivity, images/logos, theme.json manifest | HIGH |
| **AI Onboarding App**    | 50% done   | models.py, views.py                  | apps.py, urls.py, admin.py, __init__.py, migrations/, HTML templates (start.html, results.html), signals.py | HIGH |
| **Partner Ecosystem App**| 0% done    | Empty directory                      | Full Django app: models, views, urls, admin, templates, migrations | MEDIUM |
| **District Taxonomy App**| 0% done    | Referenced in CLAUDE.md only         | Full Django app or management command for district setup     | MEDIUM |
| **Terraform (AWS IaC)**  | 0% done    | Empty directory                      | main.tf, rds.tf, s3.tf, cloudfront.tf, variables.tf, outputs.tf, tfvars example | MEDIUM |
| **Kubernetes/EKS**       | 0% done    | Empty directory                      | Helm chart, HPA configs, deploy-k8s.sh                      | LOW |
| **CI/CD Pipelines**      | 0% done    | Referenced in CLAUDE.md              | .github/workflows/deploy-production.yml, deploy-staging.yml | MEDIUM |
| **Documentation**        | 70% done   | 4 of 6 docs written                  | 03-custom-theme.md (referenced but missing), 05-partner-onboarding.md (referenced but missing) | LOW |
| **Deploy Script**        | 90% done   | Full deploy.sh with preflight checks | deploy-k8s.sh skeleton                                       | LOW |
| **Consolidate Script**   | 100% done  | Full consolidation script            | —                                                            | — |

---

## Critical Path (must fix before `tutor local start` works)

1. **Tutor Plugin** – Must be a proper pip-installable package with `pyproject.toml` and entry point `tutor.plugin.v1`
2. **AI Onboarding App** – Missing `urls.py` means the URL patterns in plugin.py will fail
3. **Theme HTML** – Without Mako/HTML templates, the CSS has no structure to style

---

## Detailed Gap Breakdown

### Tutor Plugin (`tutor/plugins/chronopoli/`)
**Current:** Single `plugin.py` at the wrong path (should be inside `tutorchronopoli/` package)
**Needed:**
- `pyproject.toml` with `[project.entry-points."tutor.plugin.v1"]`
- `tutorchronopoli/__init__.py`
- `tutorchronopoli/__about__.py`
- `tutorchronopoli/plugin.py` (move + refactor existing)
- `tutorchronopoli/patches/openedx-lms-common-settings`
- `tutorchronopoli/patches/openedx-lms-production-settings`
- `tutorchronopoli/templates/chronopoli/tasks/lms/init` (district setup script)

### AI Onboarding (`plugins/ai-onboarding/`)
**Current:** models.py + views.py (solid logic, correct patterns)
**Needed:**
- `__init__.py`
- `apps.py` (Django AppConfig: `chronopoli_onboarding`)
- `urls.py` (wire up the 3 views + API endpoint)
- `admin.py` (register OnboardingProfile)
- `signals.py` (post-registration redirect to onboarding)
- `migrations/__init__.py` + `0001_initial.py`
- `templates/chronopoli/onboarding/start.html`
- `templates/chronopoli/onboarding/results.html`

### Partner Ecosystem (`plugins/partner-ecosystem/`)
**Current:** Empty
**Needed:** Full Django app with Partner model, PartnerTrack model, admin, views

### Terraform (`infrastructure/terraform/`)
**Current:** Empty directory
**Needed:** Complete IaC for Phase 1 EC2 deployment

---

## Priority Order for This Session

1. Tutor plugin restructure → pip installable
2. AI onboarding app completion → full Django app
3. Partner ecosystem app skeleton
4. Terraform skeleton
5. Gap in documentation (low priority, deferred)
6. Kubernetes (Phase 2, deferred)
