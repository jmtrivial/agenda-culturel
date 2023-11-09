from django import template
from django.utils.safestring import mark_safe

from django.templatetags.static import static
from agenda_culturel.models import Event
from django.db.models import Q

register = template.Library()

@register.filter
def in_date(event, date):
    return event.filter((Q(start_day__lte=date) & Q(end_day__gte=date)) | (Q(end_day=None) & Q(start_day=date)))

@register.simple_tag
def nb_draft_events():
    return Event.objects.filter(status=Event.STATUS.DRAFT).count()

@register.filter
def can_show_start_time(event):
    return event.start_time and (not event.end_day or event.end_day == event.start_day)


@register.filter
def need_complete_display(event, display):
    return event.end_day and event.end_day != event.start_day and (event.start_time or event.end_time or display == "in list by day")


def picto_from_name(name, datatooltip=""):
    return mark_safe('<span data-tooltip="' + datatooltip + '"><svg width="1em" height="1em" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' + \
        '<use href="' + static("images/feather-sprite.svg") + '#' + name + '" />' + \
        '</svg></span>')


@register.filter
def picto_status(event):
    if event.is_draft():
        return picto_from_name("eye-off", "Brouillon")
    elif event.is_trash():
        return picto_from_name("trash", "À la poubelle")
    else:
        return ""

