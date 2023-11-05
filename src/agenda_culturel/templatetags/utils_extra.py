from django import template
from django.utils.safestring import mark_safe

from urllib.parse import urlparse

register = template.Library()


@register.filter
def hostname(url):
    obj = urlparse(url)
    return mark_safe(obj.hostname)