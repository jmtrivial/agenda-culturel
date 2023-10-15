from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import slugify  # new
from django.urls import reverse

from django.template.defaultfilters import date as _date
from datetime import datetime


class Event(models.Model):

    class STATUS(models.TextChoices): 
        PUBLISHED = "published", _("Published")
        TRASH = "trash", _("Trash")
        DRAFT = "draft", _("Draft")

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    title = models.CharField(verbose_name=_('Title'), help_text=_('Short title'), max_length=512)

    status = models.CharField(_("Status"), max_length=20, choices=STATUS.choices, default=STATUS.PUBLISHED)

    start_day = models.DateField(verbose_name=_('Day of the event'), help_text=_('Day of the event'))
    start_time = models.TimeField(verbose_name=_('Starting time'), help_text=_('Starting time'), blank=True, null=True)

    end_day = models.DateField(verbose_name=_('End day of the event'), help_text=_('End day of the event, only required if different from the start day.'), blank=True, null=True)
    end_time = models.TimeField(verbose_name=_('Final time'), help_text=_('Final time'), blank=True, null=True)

    location = models.CharField(verbose_name=_('Location'), help_text=_('Address of the event'), max_length=512)

    description = models.TextField(verbose_name=_('Description'), help_text=_('General description of the event'), blank=True, null=True)

    image = models.URLField(verbose_name=_('Illustration'), help_text=_("URL of the illustration image"), max_length=200, blank=True, null=True)
    image_alt = models.CharField(verbose_name=_('Illustration description'), help_text=_('Alternative text used by screen readers for the image'), blank=True, null=True, max_length=512)

    reference_urls = ArrayField(models.URLField(max_length=512), verbose_name=_('URLs'), help_text=_("List of all the urls where this event can be found."), blank=True, null=True)

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