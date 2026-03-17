"""
Chronopoli Partner Ecosystem – Views
"""
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from .models import Partner, PartnerTrack


def partner_list(request):
    """List all active partners."""
    partners = Partner.objects.filter(is_active=True)
    return render(request, "chronopoli/partners/list.html", {
        "partners": partners,
    })


def partner_detail(request, slug):
    """Show a partner and their tracks."""
    partner = get_object_or_404(Partner, slug=slug, is_active=True)
    tracks = partner.tracks.filter(is_published=True)
    return render(request, "chronopoli/partners/detail.html", {
        "partner": partner,
        "tracks": tracks,
    })


def api_partners(request):
    """API: list active partners with their tracks."""
    partners = Partner.objects.filter(is_active=True).prefetch_related("tracks")
    data = []
    for p in partners:
        data.append({
            "name": p.name,
            "slug": p.slug,
            "tier": p.tier,
            "districts": p.districts,
            "tracks": [
                {"name": t.name, "district": t.district_code, "course_key": t.course_key}
                for t in p.tracks.filter(is_published=True)
            ],
        })
    return JsonResponse({"partners": data})
