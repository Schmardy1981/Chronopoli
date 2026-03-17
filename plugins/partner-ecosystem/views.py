"""
Chronopoli Partner Ecosystem – Views
"""
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from .models import Partner, PartnerTrack


@require_GET
def partner_list(request):
    """List all active partners."""
    partners = Partner.objects.filter(is_active=True)
    return render(request, "chronopoli/partners/list.html", {
        "partners": partners,
    })


@require_GET
def partner_detail(request, slug):
    """Show a partner and their tracks."""
    partner = get_object_or_404(Partner, slug=slug, is_active=True)
    tracks = partner.tracks.filter(is_published=True)
    return render(request, "chronopoli/partners/detail.html", {
        "partner": partner,
        "tracks": tracks,
    })


@require_GET
def api_partners(request):
    """API: list active partners with their tracks."""
    published_tracks = Prefetch(
        "tracks",
        queryset=PartnerTrack.objects.filter(is_published=True),
        to_attr="published_tracks",
    )
    partners = Partner.objects.filter(is_active=True).prefetch_related(published_tracks)
    data = []
    for p in partners:
        data.append({
            "name": p.name,
            "slug": p.slug,
            "tier": p.tier,
            "districts": p.districts,
            "tracks": [
                {"name": t.name, "district": t.district_code, "course_key": t.course_key}
                for t in p.published_tracks
            ],
        })
    return JsonResponse({"partners": data})
