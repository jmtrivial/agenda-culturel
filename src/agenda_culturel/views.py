from django.shortcuts import render
from django.views.generic import ListView, DetailView, FormView

from .forms import EventSubmissionModelForm
from .celery import create_event_from_submission

from .models import Event
from django.utils import timezone
from enum import StrEnum

from django.utils.translation import gettext as _


class DisplayModes(StrEnum):
    this_week = _("this_week")
    this_weekend = _("this_weekend")
    next_week = _("next_week")
    this_month = _("this_month")
    next_month = _("next_month")

def view_interval(request, mode):
    
    context = {}
    return render(request, 'agenda_culturel/list.html', context)


class EventListView(ListView):
    model = Event
    template_name = "agenda_culturel/home.html"



class EventDetailView(DetailView):
    model = Event
    template_name = "agenda_culturel/event.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        return context


class EventSubmissionFormView(FormView):
    form_class = EventSubmissionModelForm
    template_name = "agenda_culturel/submission.html"
    success_url = "/"

    def form_valid(self, form):
        form.save()
        self.create_event(form.cleaned_data)

        return super().form_valid(form)

    def create_event(self, valid_data):
        url = valid_data["url"]
        create_event_from_submission.delay(url)
