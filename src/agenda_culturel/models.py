from django.db import models
from django_better_admin_arrayfield.models.fields import ArrayField
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import slugify  # new
from django.urls import reverse
from colorfield.fields import ColorField

from django.template.defaultfilters import date as _date
from datetime import datetime


class Category(models.Model):

    COLOR_PALETTE = [
        ("#ea5545", "color 1"),
        ("#f46a9b", "color 2"),
        ("#ef9b20", "color 3"),
        ("#edbf33", "color 4"),
        ("#ede15b", "color 5"),
        ("#bdcf32", "color 6"),
        ("#87bc45", "color 7"),
        ("#27aeef", "color 8"),
        ("#b33dc6", "color 9")]

    name = models.CharField(verbose_name=_('Name'), help_text=_('Category name'), max_length=512)
    codename = models.CharField(verbose_name=_('Short name'), help_text=_('Short name of the category'), max_length=3)
    color = ColorField(verbose_name=_('Color'), help_text=_('Color used as background for the category'), blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.color is None:
            existing_colors = [c.color for c in Category.objects.all()]
            if len(existing_colors) > len(Category.COLOR_PALETTE):
                self.color = "#CCCCCC"
            else:
                for c, n in Category.COLOR_PALETTE:
                    if c not in existing_colors:
                        self.color = c
                        break
            if self.color is None:
                self.color = "#CCCCCC"

        super(Category, self).save(*args, **kwargs)

    def css_class(self):
        return "cat-" + str(self.id)


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

class Event(models.Model):

    class STATUS(models.TextChoices): 
        PUBLISHED = "published", _("Published")
        TRASH = "trash", _("Trash")
        DRAFT = "draft", _("Draft")

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    title = models.CharField(verbose_name=_('Title'), help_text=_('Short title'), max_length=512)

    status = models.CharField(_("Status"), max_length=20, choices=STATUS.choices, default=STATUS.PUBLISHED)

    category = models.ForeignKey(Category, verbose_name=_('Category'), help_text=_('Category of the event'), null=True, on_delete=models.SET_NULL)

    start_day = models.DateField(verbose_name=_('Day of the event'), help_text=_('Day of the event'))
    start_time = models.TimeField(verbose_name=_('Starting time'), help_text=_('Starting time'), blank=True, null=True)

    end_day = models.DateField(verbose_name=_('End day of the event'), help_text=_('End day of the event, only required if different from the start day.'), blank=True, null=True)
    end_time = models.TimeField(verbose_name=_('Final time'), help_text=_('Final time'), blank=True, null=True)

    location = models.CharField(verbose_name=_('Location'), help_text=_('Address of the event'), max_length=512)

    description = models.TextField(verbose_name=_('Description'), help_text=_('General description of the event'), blank=True, null=True)

    image = models.URLField(verbose_name=_('Illustration'), help_text=_("URL of the illustration image"), max_length=200, blank=True, null=True)
    image_alt = models.CharField(verbose_name=_('Illustration description'), help_text=_('Alternative text used by screen readers for the image'), blank=True, null=True, max_length=512)

    reference_urls = ArrayField(models.URLField(max_length=512), verbose_name=_('URLs'), help_text=_("List of all the urls where this event can be found."), blank=True, null=True)

    tags = ArrayField(models.CharField(max_length=64), verbose_name=_('Tags'), help_text=_("A list of tags that describe the event."), blank=True, null=True)

    def get_absolute_url(self):
        return reverse("view_event", kwargs={"pk": self.pk, "extra": self.title})

    def __str__(self):
        return _date(self.start_day) + ": " + self.title

    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')


class EventSubmissionForm(models.Model):
    url = models.URLField(max_length=512, verbose_name=_('URL'), help_text=_("URL where this event can be found."))

    class Meta:
        db_table = "eventsubmissionform"
        verbose_name = _("Event submission form")
        verbose_name_plural = _("Event submissions forms")

    def __str__(self):
        return self.url