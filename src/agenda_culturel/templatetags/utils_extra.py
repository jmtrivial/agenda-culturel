from django import template
from django.utils.safestring import mark_safe

from urllib.parse import urlparse
from datetime import timedelta, date
from django.urls import reverse_lazy

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


@register.filter
def calendar_classes(d, fixed_style):
    result = ""
    if not fixed_style:
        if d.is_in_past():
            result += " past"
        if d.is_today():
            result += " today"
    if not d.on_requested_interval:
        result += " other_month"
    return result


@register.filter
def url_day(d):
    return reverse_lazy("day_view", kwargs={"year": d.year, "month": d.month, "day": d.day})