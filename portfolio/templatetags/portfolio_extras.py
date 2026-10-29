import os

from django import template
from django.conf import settings
from django.templatetags.static import static as static_url

register = template.Library()


@register.simple_tag
def static_v(path):
    """Like {% static %}, but appends a `?v=<mtime>` cache-busting query
    string based on the source file's last-modified time, so browsers fetch
    the new version immediately after a CSS/JS change instead of serving a
    stale cached copy."""
    url = static_url(path)
    source_path = os.path.join(settings.BASE_DIR, 'static', path)
    try:
        version = int(os.path.getmtime(source_path))
    except OSError:
        return url
    separator = '&' if '?' in url else '?'
    return f'{url}{separator}v={version}'
