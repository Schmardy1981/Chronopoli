"""
Chronopoli Symposia – Signals

Signal handlers for Round Table lifecycle events.
"""
import logging

from django.dispatch import receiver

log = logging.getLogger(__name__)

try:
    from django.db.models.signals import post_save
    HAVE_SIGNALS = True
except ImportError:
    HAVE_SIGNALS = False
    log.info("Django signals not available – running outside Django context")
