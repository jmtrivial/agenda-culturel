from django import template
from django.utils.safestring import mark_safe
from django.urls import reverse_lazy

register = template.Library()

@register.filter
def tag_button(tag, link=False):
    if link:
        return mark_safe('<a href="' + reverse_lazy('view_tag', {"tag": tag}) +'" role="button" class="small-cat">' +  tag + '</a>')
    else:
        return mark_safe('<span role="button" class="small-cat">' +  tag + '</span>')