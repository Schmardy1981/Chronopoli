"""
Chronopoli – Custom Tutor Plugin
Adds Chronopoli-specific configuration to OpenEdX/Tutor deployments.
"""
from glob import glob
import os
import pkg_resources
from tutor import hooks

# Plugin name
PLUGIN_NAME = "chronopoli"

# ============================================================
# PATCH: LMS common settings
# ============================================================
hooks.Filters.CONFIG_DEFAULTS.add_items(
    [
        # Platform identity
        ("PLATFORM_NAME", "Chronopoli"),
        ("PLATFORM_DESCRIPTION", "The Global Knowledge City for AI, Blockchain & Digital Trust"),
        
        # Chronopoli-specific settings
        ("CHRONOPOLI_VERSION", "1.0.0"),
        ("CHRONOPOLI_SUPPORT_EMAIL", "support@chronopoli.io"),
        ("CHRONOPOLI_PARTNER_CONTACT", "partners@chronopoli.io"),
        
        # Districts config
        ("CHRONOPOLI_DISTRICTS", [
            {"code": "CHRON-AI",   "name": "AI District",             "color": "#6C63FF"},
            {"code": "CHRON-DA",   "name": "Digital Assets District",  "color": "#F59E0B"},
            {"code": "CHRON-GOV",  "name": "Governance District",      "color": "#10B981"},
            {"code": "CHRON-COMP", "name": "Compliance District",      "color": "#3B82F6"},
            {"code": "CHRON-INV",  "name": "Investigation District",   "color": "#EF4444"},
            {"code": "CHRON-RISK", "name": "Risk & Trust District",    "color": "#8B5CF6"},
        ]),
        
        # AI onboarding
        ("CHRONOPOLI_AI_ONBOARDING_ENABLED", True),
        ("CHRONOPOLI_AI_ONBOARDING_QUESTIONS", 5),
    ]
)

# ============================================================
# PATCH: LMS Django settings (added to lms/env/common.py)
# ============================================================
hooks.Filters.ENV_PATCHES.add_items(
    [
        (
            "openedx-lms-common-settings",
            """
# ============================================================
# CHRONOPOLI SETTINGS
# ============================================================

PLATFORM_NAME = "Chronopoli"
PLATFORM_DESCRIPTION = "The Global Knowledge City for AI, Blockchain & Digital Trust"

# Chronopoli Districts
CHRONOPOLI_DISTRICTS = {{ CHRONOPOLI_DISTRICTS | tojson }}

# Certificates
CERT_HTML_VIEW_ENABLED = True
CERTIFICATES_HTML_VIEW = True

# Course Discovery
COURSE_CATALOG_API_URL = "https://{{ LMS_HOST }}/api/catalog/v1/"

# Partner content permissions
CHRONOPOLI_PARTNER_CONTENT_ENABLED = True

# AI Onboarding
CHRONOPOLI_AI_ONBOARDING_ENABLED = {{ CHRONOPOLI_AI_ONBOARDING_ENABLED }}

# Social sharing
SOCIAL_SHARING_SETTINGS = {
    "CERTIFICATE_FACEBOOK": True,
    "CERTIFICATE_LINKEDIN": True,
    "CERTIFICATE_EMAIL": True,
}

# Analytics (add your key when ready)
# SEGMENT_KEY = "your-segment-key"

# Custom footer links
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
# ADD CHRONOPOLI URLS to LMS
# ============================================================
hooks.Filters.ENV_PATCHES.add_items(
    [
        (
            "openedx-lms-urls",
            """
# Chronopoli custom endpoints
url(r'^chronopoli/', include('chronopoli_platform.urls')),
url(r'^api/chronopoli/', include('chronopoli_platform.api.urls')),
""",
        ),
    ]
)

# ============================================================
# DOCKER COMPOSE – Add any Chronopoli services
# ============================================================
hooks.Filters.COMPOSE_LOCAL_JOBS_OVERRIDES.add_items(
    [
        # Future: add Chronopoli worker service here
    ]
)
