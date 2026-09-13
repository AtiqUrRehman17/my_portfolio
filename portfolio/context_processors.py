from .models import Profile


def site_profile(request):
    """Make the single portfolio profile available to every template."""
    return {'site_profile': Profile.objects.first()}
