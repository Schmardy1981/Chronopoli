"""
Chronopoli Company Academy – Partner Subdomain Middleware

Resolves the current request's subdomain and attaches the corresponding
Partner instance (if any) to the request object.
"""
import logging

logger = logging.getLogger(__name__)

# Subdomains reserved for core platform services — never treated as partner slugs.
SYSTEM_SUBDOMAINS = [
    "learn",
    "studio",
    "community",
    "video",
    "slides",
    "preview",
    "www",
]


class PartnerSubdomainMiddleware:
    """
    Sets ``request.partner`` to the matching Partner or None,
    and ``request.is_academy`` to True when a partner academy is active.

    Expected hostname pattern: ``<partner-slug>.chronopoli.io``
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.partner = None
        request.is_academy = False

        host = request.get_host().split(":")[0]  # strip port
        parts = host.split(".")

        # Need at least <sub>.<domain>.<tld>
        if len(parts) >= 3:
            subdomain = parts[0].lower()

            if subdomain not in SYSTEM_SUBDOMAINS:
                try:
                    from chronopoli_partners.models import Partner
                    partner = Partner.objects.filter(
                        slug=subdomain, is_active=True
                    ).first()

                    if partner:
                        request.partner = partner
                        request.is_academy = True
                        logger.debug(
                            "Academy subdomain resolved: %s → %s",
                            subdomain,
                            partner.name,
                        )
                except ImportError:
                    logger.warning(
                        "chronopoli_partners app not installed; "
                        "subdomain resolution skipped."
                    )
                except Exception:
                    logger.exception(
                        "Error resolving partner subdomain: %s", subdomain
                    )

        return self.get_response(request)
