from django import template
from django.utils.safestring import mark_safe

from agenda_culturel.models import Event
from django.db.models import Q

register = template.Library()

@register.filter
def in_date(event, date):
    return event.filter((Q(start_day__lte=date) & Q(end_day__gte=date)) | (Q(end_day=None) & Q(start_day=date)))
