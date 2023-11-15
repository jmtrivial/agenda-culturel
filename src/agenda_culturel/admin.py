from django.contrib import admin
from django import forms
from .models import Event, EventSubmissionForm, Category, StaticContent
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin
from django_better_admin_arrayfield.forms.widgets import DynamicArrayWidget
from django_better_admin_arrayfield.models.fields import DynamicArrayField


admin.site.register(EventSubmissionForm)
admin.site.register(Category)
admin.site.register(StaticContent)


class URLWidget(DynamicArrayWidget):
    def __init__(self, *args, **kwargs):
        kwargs['subwidget_form'] = forms.URLField()
        super().__init__(*args, **kwargs)

@admin.register(Event)
class Eventdmin(admin.ModelAdmin, DynamicArrayMixin):
    
    formfield_overrides = {
        DynamicArrayField: {'urls': URLWidget},
    }