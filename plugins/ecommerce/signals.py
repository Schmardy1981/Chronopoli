"""
Chronopoli E-Commerce Signals

Listens for OpenEdX enrollment changes to track paid vs free enrollments.
"""

import logging

from django.dispatch import receiver

logger = logging.getLogger(__name__)

try:
    from common.djangoapps.student.models import CourseEnrollment
    from django.db.models.signals import post_save

    HAVE_ENROLLMENT = True
except ImportError:
    HAVE_ENROLLMENT = False
    logger.info("OpenEdX enrollment model not available — ecommerce signals disabled")


if HAVE_ENROLLMENT:

    @receiver(post_save, sender=CourseEnrollment)
    def track_enrollment(sender, instance, created, **kwargs):
        """
        Track new enrollments. If a Purchase record exists for this
        user+course, mark it as enrolled.
        """
        if not created:
            return

        try:
            from .models import Purchase

            purchase = Purchase.objects.filter(
                user=instance.user,
                course_key=str(instance.course_id),
                status="completed",
                enrolled=False,
            ).first()

            if purchase:
                purchase.enrolled = True
                purchase.save(update_fields=["enrolled"])
                logger.info(
                    "Purchase enrollment confirmed: %s in %s",
                    instance.user.username, instance.course_id,
                )
        except Exception as e:
            logger.warning("Error tracking enrollment: %s", e)
