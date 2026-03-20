"""
Chronopoli Company Academy – Signals

Listens for OpenEdX certificate creation events and checks whether the
user has completed all required courses in any Learning Pathway.
If so, awards the corresponding badge and runs the talent pipeline.
"""
import logging

from django.dispatch import receiver

from chronopoli_academy.models import LearningPathway, PathwayStep

logger = logging.getLogger(__name__)

# Attempt to import the OpenEdX certificate signal.
# This will only be available inside the LMS runtime.
try:
    from lms.djangoapps.certificates.signals import CERTIFICATE_CREATED

    _signal_available = True
except ImportError:
    _signal_available = False
    logger.info(
        "OpenEdX CERTIFICATE_CREATED signal not available; "
        "academy auto-badge disabled."
    )


def _check_pathway_completion(user, course_key_str):
    """
    For every published pathway that includes the completed course,
    check if all required steps are now complete. If so, award badges.
    """
    from chronopoli_academy.badge_issuer import award_badge
    from chronopoli_academy.talent_pipeline import check_and_apply

    # Find pathways containing this course
    step_qs = PathwayStep.objects.filter(
        course_key=course_key_str,
        pathway__is_published=True,
    ).select_related("pathway")

    for step in step_qs:
        pathway = step.pathway
        required_steps = pathway.steps.filter(is_required=True)
        required_keys = set(required_steps.values_list("course_key", flat=True))

        # Check completions via OpenEdX grades
        completed_keys = set()
        try:
            from opaque_keys.edx.keys import CourseKey
            from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory

            for key_str in required_keys:
                try:
                    ck = CourseKey.from_string(key_str)
                    grade = CourseGradeFactory().read(user, course_key=ck)
                    if grade and grade.passed:
                        completed_keys.add(key_str)
                except Exception:
                    pass
        except ImportError:
            logger.debug("Grade API not available; cannot verify pathway completion.")
            return

        if required_keys <= completed_keys:
            # All required courses passed — award badges
            badges = pathway.badges.all()
            for badge in badges:
                try:
                    award_badge(user, badge, pathway=pathway)
                    logger.info(
                        "Awarded badge '%s' to user %s for pathway '%s'.",
                        badge.name,
                        user.username,
                        pathway.title,
                    )
                except Exception:
                    logger.exception(
                        "Failed to award badge '%s' to user %s.",
                        badge.name,
                        user.username,
                    )

            # Run talent pipeline
            try:
                check_and_apply(user, pathway)
            except Exception:
                logger.exception(
                    "Talent pipeline error for user %s, pathway '%s'.",
                    user.username,
                    pathway.title,
                )


if _signal_available:
    @receiver(CERTIFICATE_CREATED)
    def on_certificate_created(sender, user, course_key, **kwargs):
        """
        Triggered when a certificate is generated in OpenEdX.
        """
        course_key_str = str(course_key)
        logger.info(
            "Certificate created for user %s in course %s; checking pathways.",
            user.username,
            course_key_str,
        )
        _check_pathway_completion(user, course_key_str)
