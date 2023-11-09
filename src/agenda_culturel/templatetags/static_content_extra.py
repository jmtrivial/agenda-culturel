from django import template
from django.utils.safestring import mark_safe

from agenda_culturel.models import StaticContent
from django.db.models import Q

register = template.Library()

@register.simple_tag
def get_static_content_by_name(name):
    result = StaticContent.objects.filter(name=name)
    if result is None or len(result) == 0:
        return None
    else:
        return result[0]

@register.simple_tag
def concat_all(*args):
    """concatenate all args"""
    return ''.join(map(str, args))