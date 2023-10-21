from django.contrib import admin
from .models import Event, EventSubmissionForm, Category

admin.site.register(Event)
admin.site.register(EventSubmissionForm)
admin.site.register(Category)
