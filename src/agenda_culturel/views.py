from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, FormView

from .forms import EventSubmissionModelForm
from .celery import create_event_from_submission

from .models import Event, Category
from django.utils import timezone
from enum import StrEnum
from datetime import datetime, timedelta
from django.db.models import Q

from django.utils.translation import gettext_lazy as _
from django.utils.translation import activate, get_language_info
import django_filters
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required



class DisplayMode(StrEnum):
    this_week = "this week"
    this_weekend = "this weekend"
    next_week = "next week"
    next_weekend = "next weekend"
    this_month = "this month"
    next_month = "next month"

    def i18n_value(self):
        return _(self.value)

    def get_dates(self):
        now = datetime.now()
        if self in [DisplayMode.this_week, DisplayMode.next_week]:
            day = now.weekday() # 0: Monday, 6: Sunday
            start = now + timedelta(days=-day)
            if self == DisplayMode.next_week:
                start += timedelta(days=7)
            return [start + timedelta(days=x) for x in range(0, 7)]
        elif self in [DisplayMode.this_weekend, DisplayMode.next_weekend]:
            day = now.weekday() # 0: Monday, 6: Sunday
            start = now + timedelta(days=-day + 5)
            if self == DisplayMode.next_week:
                start += timedelta(days=7)
            return [start + timedelta(days=x) for x in range(0, 2)]
        elif self in [DisplayMode.this_month, DisplayMode.next_month]:
            start = now.replace(day=1)
            if self == DisplayMode.next_month:
                start = (start.replace(day=1) + timedelta(days=32)).replace(day=1)
            next_month = start.replace(day=28) + timedelta(days=4)
            end = next_month - timedelta(days=next_month.day)
            delta = end - start
            return [start + timedelta(days=x) for x in range(0, delta.days + 1)]

    def __str__(self):
        return str(self.i18n_value())


def home(request):
    # TODO: si on est au début de la semaine, on affiche la semaine en entier
    # sinon, on affiche le week-end
    # sauf si on est dimanche après 23h, on affiche la semaine prochaine
    return view_mode(request, DisplayMode.this_week.name)


def view_mode(request, mode):
    categories = Category.objects.all()
    dates = DisplayMode[mode].get_dates()
    events = Event.objects.filter(Q(start_day__lte=dates[-1]) & Q(start_day__gte=dates[0])).order_by("start_day", "start_time")
    context = {"modes": list(DisplayMode), "selected_mode": DisplayMode[mode], "categories": categories, "events": events, "dates": dates}
    return render(request, 'agenda_culturel/page-events.html', context)


def view_mode_cat(request, mode, cat_id):
    category = get_object_or_404(Category, pk=cat_id)
    categories = Category.objects.all()
    dates = DisplayMode[mode].get_dates()
    events = Event.objects.filter(start_day__lte=dates[-1], start_day__gte=dates[0], category=category).order_by("start_day", "start_time")
    context = {"modes": list(DisplayMode), "selected_mode": DisplayMode[mode], "category": category, "categories": categories, "events": events, "dates": dates}
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



class EventFilter(django_filters.FilterSet):
    tags = django_filters.CharFilter(lookup_expr='icontains')


    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('created_date', 'created_date'),
            ('modified_date', 'modified_date'),
            ('status', 'status'),
            ('title', 'title'),
            ('start_day', 'start_day'),
        ),
    )


    class Meta:
        model = Event
        fields = ['title', 'status', 'category', 'tags']

@login_required(login_url="/accounts/login/")
def event_list(request):
    filter = EventFilter(request.GET, queryset=Event.objects.all())
    paginator = Paginator(filter.qs, 10)
    page = request.GET.get('page')

    try:
        response = paginator.page(page)
    except PageNotAnInteger:
        response = paginator.page(1)
    except EmptyPage:
        response = paginator.page(paginator.num_pages)

    return render(request, 'agenda_culturel/list.html', {'filter': filter, 'paginator_filter': response})
