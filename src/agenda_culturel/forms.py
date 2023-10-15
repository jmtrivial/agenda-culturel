from django.forms import ModelForm
from django.views.generic import FormView

from .models import EventSubmissionForm


class EventSubmissionModelForm(ModelForm):
    class Meta:
        model = EventSubmissionForm
        fields = ["url"]

