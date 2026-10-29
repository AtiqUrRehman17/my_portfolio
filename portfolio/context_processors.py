from .models import Profile


def site_profile(request):
    """Make the single portfolio profile available to every template,
    fetching it at most once per request even if a view also needs it
    directly (e.g. to pass into a helper function) before rendering."""
    if not hasattr(request, '_cached_site_profile'):
        request._cached_site_profile = Profile.objects.first()
    return {'site_profile': request._cached_site_profile}
