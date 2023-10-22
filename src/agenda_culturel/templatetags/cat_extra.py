from django import template
from django.utils.safestring import mark_safe

from agenda_culturel.models import Category

register = template.Library()

def color_variant(hex_color, brightness_offset=1):
    """ takes a color like #87c95f and produces a lighter or darker variant """
    if len(hex_color) != 7:
        raise Exception("Passed %s into color_variant(), needs to be in #87c95f format." % hex_color)
    rgb_hex = [hex_color[x:x + 2] for x in [1, 3, 5]]
    new_rgb_int = [int(hex_value, 16) + brightness_offset for hex_value in rgb_hex]
    new_rgb_int = [min([255, max([0, i])]) for i in new_rgb_int] # make sure new values are between 0 and 255
    # hex() produces "0x88", we want just "88"
    return "#" + "".join([hex(i)[2:] for i in new_rgb_int])


@register.simple_tag
def css_categories():
    result = '<style type="text/css">'
    
    cats = Category.objects.all()

    for c in cats:
        result += "." + c.css_class() + " {"
        result += " background-color: " + c.color + ";"
        result += " border: 2px solid " + color_variant(c.color, -20) + ";"
        result += "}"

        result += "." + c.css_class() + ":hover {"
        result += " background-color: " + color_variant(c.color, 20) + ";"
        result += " border: 2px solid " + c.color + ";"
        result += "}"

    result += '</style>'
    return mark_safe(result)
