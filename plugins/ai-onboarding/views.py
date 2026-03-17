"""
Chronopoli AI Onboarding – Django Views
"""

import json
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET

from .models import OnboardingProfile, ONBOARDING_QUESTIONS, calculate_recommendations

logger = logging.getLogger(__name__)

# Discourse district group mapping
DISCOURSE_DISTRICT_GROUPS = {
    "CHRON-AI":   "ai-district",
    "CHRON-DA":   "digital-assets-district",
    "CHRON-GOV":  "governance-district",
    "CHRON-COMP": "compliance-district",
    "CHRON-INV":  "investigation-district",
    "CHRON-RISK": "risk-trust-district",
}


def _assign_discourse_group(username, district_code):
    """
    Add user to their primary district group on Discourse.
    Called after AI onboarding questionnaire completion.
    Fails silently if Discourse is not configured.
    """
    try:
        import requests
        from django.conf import settings

        discourse_url = getattr(settings, "DISCOURSE_BASE_URL", "")
        api_key = getattr(settings, "DISCOURSE_API_KEY", "")

        if not discourse_url or not api_key or api_key == "CHANGE_THIS_AFTER_DISCOURSE_SETUP":
            return

        group_name = DISCOURSE_DISTRICT_GROUPS.get(district_code)
        if not group_name:
            return

        headers = {"Api-Key": api_key, "Api-Username": "system"}

        resp = requests.get(
            f"{discourse_url}/groups/{group_name}.json",
            headers=headers, timeout=10,
        )
        if resp.status_code != 200:
            logger.warning("Discourse group %s not found", group_name)
            return

        group_id = resp.json()["group"]["id"]
        requests.put(
            f"{discourse_url}/groups/{group_id}/members.json",
            headers=headers, json={"usernames": username}, timeout=10,
        )
        logger.info("Assigned %s to Discourse group %s", username, group_name)
    except Exception as e:
        logger.warning("Discourse group assignment failed for %s: %s", username, e)


@login_required
def onboarding_start(request):
    """
    Step 1: Check if user needs onboarding, redirect if already done.
    """
    profile, created = OnboardingProfile.objects.get_or_create(user=request.user)
    
    if profile.onboarding_completed:
        return redirect('/dashboard')
    
    return render(request, 'chronopoli/onboarding/start.html', {
        'questions': ONBOARDING_QUESTIONS,
        'total_questions': len(ONBOARDING_QUESTIONS),
        'platform_name': 'Chronopoli',
    })


@login_required
def onboarding_submit(request):
    """
    Step 2: Process questionnaire answers and generate recommendations.
    """
    if request.method != 'POST':
        return redirect('/chronopoli/onboarding/')
    
    # Parse answers from form
    answers = {}
    for question in ONBOARDING_QUESTIONS:
        q_id = question['id']
        answers[q_id] = request.POST.get(q_id, '')
    
    # Calculate recommendations
    recommendations = calculate_recommendations(answers)
    
    # Save to profile
    profile, _ = OnboardingProfile.objects.get_or_create(user=request.user)
    profile.questionnaire_answers = answers
    profile.user_type = recommendations['user_type']
    profile.primary_district = recommendations['primary_district']
    profile.secondary_districts = recommendations['secondary_districts']
    profile.recommended_layer = recommendations['recommended_layer']
    profile.onboarding_completed = True
    profile.onboarding_completed_at = timezone.now()
    profile.save()

    # Assign user to their district group on Discourse
    _assign_discourse_group(
        request.user.username,
        recommendations['primary_district'],
    )

    return redirect('/chronopoli/onboarding/results/')


@login_required
def onboarding_results(request):
    """
    Step 3: Show personalized district + course recommendations.
    """
    try:
        profile = OnboardingProfile.objects.get(user=request.user)
    except OnboardingProfile.DoesNotExist:
        return redirect('/chronopoli/onboarding/')
    
    # District display data
    district_info = {
        'CHRON-AI':   {'name': 'AI District',             'color': '#6C63FF', 'icon': '🧠'},
        'CHRON-DA':   {'name': 'Digital Assets District', 'color': '#F59E0B', 'icon': '⛓️'},
        'CHRON-GOV':  {'name': 'Governance District',     'color': '#10B981', 'icon': '🏛️'},
        'CHRON-COMP': {'name': 'Compliance District',     'color': '#3B82F6', 'icon': '🛡️'},
        'CHRON-INV':  {'name': 'Investigation District',  'color': '#EF4444', 'icon': '🔍'},
        'CHRON-RISK': {'name': 'Risk & Trust District',   'color': '#8B5CF6', 'icon': '⚖️'},
    }
    
    primary = district_info.get(profile.primary_district, {})
    secondary = [district_info.get(d, {}) for d in profile.secondary_districts]
    
    layer_labels = {
        'entry': 'Entry Level – Start with the fundamentals',
        'professional': 'Professional – Role-specific deep dives',
        'institutional': 'Institutional – Strategic and leadership programs',
        'influence': 'Influence – Thought leadership and research',
    }
    
    return render(request, 'chronopoli/onboarding/results.html', {
        'profile': profile,
        'primary_district': primary,
        'secondary_districts': secondary,
        'layer_label': layer_labels.get(profile.recommended_layer, ''),
        'user': request.user,
    })


@require_GET
def api_onboarding_status(request):
    """
    API endpoint: check onboarding status for current user.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        profile = OnboardingProfile.objects.get(user=request.user)
        return JsonResponse({
            'completed': profile.onboarding_completed,
            'user_type': profile.user_type,
            'primary_district': profile.primary_district,
            'recommended_layer': profile.recommended_layer,
        })
    except OnboardingProfile.DoesNotExist:
        return JsonResponse({'completed': False})
