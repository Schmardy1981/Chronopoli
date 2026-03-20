"""
Chronopoli – Custom Tutor Plugin
Adds Chronopoli-specific configuration to OpenEdX/Tutor deployments.

Discovery: tutor.plugin.v1 entry point in pyproject.toml
"""
from __future__ import annotations

import importlib_resources
from glob import glob
import os

from tutor import hooks

from .__about__ import __version__

# ============================================================
# CONFIG DEFAULTS (non-secret values)
# ============================================================
hooks.Filters.CONFIG_DEFAULTS.add_items(
    [
        ("CHRONOPOLI_VERSION", __version__),
        ("PLATFORM_NAME", "Chronopoli"),
        ("PLATFORM_DESCRIPTION", "The Global Knowledge City for AI, Blockchain & Digital Trust"),
        ("CHRONOPOLI_SUPPORT_EMAIL", "support@chronopoli.io"),
        ("CHRONOPOLI_PARTNER_CONTACT", "partners@chronopoli.io"),
        ("CHRONOPOLI_DISTRICTS", [
            {"code": "CHRON-AI",   "name": "AI District",            "color": "#6C63FF"},
            {"code": "CHRON-DA",   "name": "Digital Assets District", "color": "#F59E0B"},
            {"code": "CHRON-GOV",  "name": "Governance District",     "color": "#10B981"},
            {"code": "CHRON-COMP", "name": "Compliance District",     "color": "#3B82F6"},
            {"code": "CHRON-INV",  "name": "Investigation District",  "color": "#EF4444"},
            {"code": "CHRON-RISK", "name": "Risk & Trust District",   "color": "#8B5CF6"},
            {"code": "CHRON-ET",   "name": "Emerging Tech District", "color": "#06B6D4"},
        ]),
        ("CHRONOPOLI_AI_ONBOARDING_ENABLED", True),
        ("CHRONOPOLI_AI_ONBOARDING_QUESTIONS", 5),
        # Non-secret service defaults
        ("DISCOURSE_BASE_URL", "https://community.chronopoli.io"),
        ("OPENCAST_LTI_KEY", "chronopoli-openedx"),
        ("OPENCAST_BASE_URL", "https://video.chronopoli.io"),
    ]
)

# ============================================================
# CONFIG UNIQUE – secrets auto-generated on `tutor config save`
# ============================================================
hooks.Filters.CONFIG_UNIQUE.add_items(
    [
        ("DISCOURSE_SSO_SECRET", "{{ 64|random_string }}"),
        ("OPENCAST_LTI_SECRET", "{{ 32|random_string }}"),
    ]
)

# ============================================================
# CONFIG OVERRIDES – secrets that must be set manually
# ============================================================
hooks.Filters.CONFIG_OVERRIDES.add_items(
    [
        ("DISCOURSE_API_KEY", ""),
        ("STRIPE_SECRET_KEY", ""),
        ("STRIPE_PUBLISHABLE_KEY", ""),
        ("STRIPE_WEBHOOK_SECRET", ""),
        ("STRIPE_CONNECT_CLIENT_ID", ""),
    ]
)

# ============================================================
# TEMPLATE ROOTS & TARGETS
# ============================================================
hooks.Filters.ENV_TEMPLATE_ROOTS.add_item(
    str(importlib_resources.files("tutorchronopoli") / "templates")
)

hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
    [
        ("chronopoli/tasks", "plugins"),
    ]
)

# ============================================================
# PATCHES (loaded from tutorchronopoli/patches/ directory)
# ============================================================
for path in glob(str(importlib_resources.files("tutorchronopoli") / "patches" / "*")):
    with open(path, encoding="utf-8") as patch_file:
        patch_name = os.path.basename(path)
        hooks.Filters.ENV_PATCHES.add_item(
            (patch_name, patch_file.read())
        )

# ============================================================
# LMS SETTINGS – inject Chronopoli Django apps into OpenEdX LMS
# ============================================================
hooks.Filters.ENV_PATCHES.add_items(
    [
        (
            "openedx-lms-common-settings",
            """
# ============================================================
# CHRONOPOLI PLATFORM SETTINGS
# ============================================================

PLATFORM_NAME = "{{ PLATFORM_NAME }}"
PLATFORM_DESCRIPTION = "{{ PLATFORM_DESCRIPTION }}"

# Chronopoli Django apps
INSTALLED_APPS.append("chronopoli_onboarding")
INSTALLED_APPS.append("chronopoli_partners")
INSTALLED_APPS.append("chronopoli_discourse_sso")
INSTALLED_APPS.append("chronopoli_ecommerce")

# Chronopoli Districts config
CHRONOPOLI_DISTRICTS = {{ CHRONOPOLI_DISTRICTS | tojson }}

# Certificates
CERT_HTML_VIEW_ENABLED = True

# Partner content
CHRONOPOLI_PARTNER_CONTENT_ENABLED = True

# AI Onboarding
CHRONOPOLI_AI_ONBOARDING_ENABLED = {{ CHRONOPOLI_AI_ONBOARDING_ENABLED | tojson }}

# Discourse SSO Integration
DISCOURSE_SSO_SECRET = "{{ DISCOURSE_SSO_SECRET }}"
DISCOURSE_BASE_URL = "{{ DISCOURSE_BASE_URL }}"
DISCOURSE_API_KEY = "{{ DISCOURSE_API_KEY }}"

# Opencast LTI Integration
OPENCAST_LTI_KEY = "{{ OPENCAST_LTI_KEY }}"
OPENCAST_LTI_SECRET = "{{ OPENCAST_LTI_SECRET }}"
OPENCAST_BASE_URL = "{{ OPENCAST_BASE_URL }}"

# Stripe Payment Integration
STRIPE_SECRET_KEY = "{{ STRIPE_SECRET_KEY }}"
STRIPE_PUBLISHABLE_KEY = "{{ STRIPE_PUBLISHABLE_KEY }}"
STRIPE_WEBHOOK_SECRET = "{{ STRIPE_WEBHOOK_SECRET }}"
STRIPE_CONNECT_CLIENT_ID = "{{ STRIPE_CONNECT_CLIENT_ID }}"

# Enable LTI Provider
FEATURES["ENABLE_LTI_PROVIDER"] = True

# Social sharing for certificates
SOCIAL_SHARING_SETTINGS = {
    "CERTIFICATE_FACEBOOK": True,
    "CERTIFICATE_LINKEDIN": True,
    "CERTIFICATE_EMAIL": True,
}

# Footer links
MKTG_URL_LINK_MAP = {
    "ABOUT": "about",
    "PRIVACY": "privacy",
    "TERMS_OF_SERVICE": "tos",
}
""",
        ),
    ]
)

# ============================================================
# CMS SETTINGS – apps needed in Studio for migrations
# ============================================================
hooks.Filters.ENV_PATCHES.add_items(
    [
        (
            "openedx-cms-common-settings",
            """
# Chronopoli Django apps (needed for migrations)
INSTALLED_APPS.append("chronopoli_onboarding")
INSTALLED_APPS.append("chronopoli_partners")
INSTALLED_APPS.append("chronopoli_discourse_sso")
INSTALLED_APPS.append("chronopoli_ecommerce")
""",
        ),
    ]
)

# ============================================================
# URL PATTERNS – add Chronopoli URLs to LMS
# ============================================================
hooks.Filters.ENV_PATCHES.add_items(
    [
        (
            "openedx-lms-urls",
            """
# Chronopoli custom endpoints
urlpatterns += [
    path("chronopoli/", include("chronopoli_onboarding.urls")),
    path("chronopoli/partners/", include("chronopoli_partners.urls")),
    path("auth/discourse/", include("chronopoli_discourse_sso.urls")),
    path("chronopoli/ecommerce/", include("chronopoli_ecommerce.urls")),
]
""",
        ),
    ]
)
