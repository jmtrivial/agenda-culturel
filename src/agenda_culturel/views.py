from django.shortcuts import render
from django.views.generic import ListView, DetailView
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