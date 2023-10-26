from django import template
from django.utils.safestring import mark_safe

from agenda_culturel.models import Category
import statistics
import colorsys

register = template.Library()


def html_to_rgb(hex_color):
    """ takes a color like #87c95f and produces a desaturate color """
    if len(hex_color) != 7:
        raise Exception("Passed %s into color_variant(), needs to be in #87c95f format." % hex_color)

    rgb_hex = [hex_color[x:x + 2] for x in [1, 3, 5]]
    rgb_in = [int(hex_value, 16) for hex_value in rgb_hex]

    return [x / 255 for x in rgb_in]

def rgb_to_html(rgb):
    new_rgb_int = [min([255, max([0, int(i * 255)])]) for i in rgb] # make sure new values are between 0 and 255
    
    # hex() produces "0x88", we want just "88"
    return "#" + "".join([("0" + hex(i)[2:])[-2:] for i in new_rgb_int])


def get_relative_luminance(hex_color):

    rgb = html_to_rgb(hex_color)
    R = rgb[0] / 12.92 if rgb[0] <= 0.04045 else ((rgb[0] + 0.055) / 1.055) ** 2.4
    G = rgb[1] / 12.92 if rgb[1] <= 0.04045 else ((rgb[1] + 0.055) / 1.055) ** 2.4
    B = rgb[2] / 12.92 if rgb[2] <= 0.04045 else ((rgb[2] + 0.055) / 1.055) ** 2.4

    return 0.2126 * R + 0.7152 * G + 0.0722 * B

def adjust_lightness_saturation(hex_color, shift_lightness = 0.0, scale_saturation=1):
    rgb = html_to_rgb(hex_color)

    h, l, s = colorsys.rgb_to_hls(*rgb)

    l += shift_lightness
    s *= scale_saturation

    r, g, b =  colorsys.hls_to_rgb(h, l, s)

    return rgb_to_html([r, g, b])


def background_color_adjust_color(color, alpha = 1):
    result = " background-color: " + color + ("0" + hex(int(alpha * 255))[2:])[-2:] + ";"
    if get_relative_luminance(color) < .5:
        result += " color: #fff;"
    else:
        result += " color: #000;"
    return result


@register.simple_tag
def css_categories():
    result = '<style type="text/css">'
    
    cats = Category.objects.all()

    for c in cats:
        result += "." + c.css_class() + " {"
        result += background_color_adjust_color(adjust_lightness_saturation(c.color, .2, 0.8), 0.8)
        result += "}"

        result += "a." + c.css_class() + ":hover {"
        result += background_color_adjust_color(adjust_lightness_saturation(c.color, 0.1, 1.2))
        result += "}"

        result += "." + c.css_class() + ".selected {"
        result += background_color_adjust_color(c.color)
        result += "}"


    result += '</style>'
    return mark_safe(result)
