from django import template
from django.utils.safestring import mark_safe

from urllib.parse import urlparse
from datetime import timedelta, date

register = template.Library()


@register.filter
def hostname(url):
    obj = urlparse(url)
    return mark_safe(obj.hostname)


@register.filter
def add_de(txt):
    return ("d'" if txt[0].lower() in ['a', 'e', 'i', 'o', 'u', 'y'] else "de ") + txt

@register.filter
def week(d):
    return d.isocalendar()[1]

@register.filter
def shift_day(d, shift):
    return d + timedelta(days=shift)

@register.filter
def first_day_of_this_week(d):
    return date.fromisocalendar(d.year, week(d), 1)

@register.filter
def last_day_of_this_week(d):
    return date.fromisocalendar(d.year, week(d), 7)    
