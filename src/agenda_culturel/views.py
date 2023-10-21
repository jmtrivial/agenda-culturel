from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, FormView

from .forms import EventSubmissionModelForm
from .celery import create_event_from_submission

from .models import Event, Category
from django.utils import timezone
from enum import StrEnum

from django.utils.translation import gettext as _


class DisplayMode(StrEnum):
    this_week = _("this week")
    this_weekend = _("this weekend")
    next_week = _("next week")
    this_month = _("this month")
    next_month = _("next month")


def home(request):
    # TODO: si on est au début de la semaine, on affiche la semaine en entier
    # sinon, on affiche le week-end
    # sauf si on est dimanche après 23h, on affiche la semaine prochaine
    return view_mode(request, DisplayMode.this_week)


def view_mode(request, mode):
    categories = Category.objects.all()
    context = {"modes": list(DisplayMode), "selected_mode": mode, "categories": categories}
    # TODO: select matching events
    return render(request, 'agenda_culturel/page-events.html', context)


def view_mode_cat(request, mode, cat_id):
    category = get_object_or_404(Category, pk=cat_id)
    categories = Category.objects.all()
    # TODO: select matching events
    context = {"modes": list(DisplayMode), "selected_mode": mode, "category": category, "categories": categories}
    return render(request, 'agenda_culturel/page-events.html', context)



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
