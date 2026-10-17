from pathlib import Path

from django import template
from django.conf import settings
from django.templatetags.static import static
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def icon(name):
    return format_html('<svg class="i" aria-hidden="true"><use href="#i-{}"/></svg>', name)


@register.simple_tag
def asset(path):
    """URL statique versionnée par la date de modification du fichier."""
    try:
        stamp = int(Path(settings.BASE_DIR, "static", path).stat().st_mtime)
    except OSError:
        stamp = 0
    return f"{static(path)}?v={stamp}"
