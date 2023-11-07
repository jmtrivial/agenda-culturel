from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import EventSubmissionModelForm
from .celery import create_event_from_submission

from .models import Event, Category
from django.utils import timezone
from enum import StrEnum
from datetime import datetime, timedelta, date
import calendar
from django.db.models import Q

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.utils.translation import activate, get_language_info
import django_filters
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

import unicodedata


def daterange(start, end, step=timedelta(1)):
    if end is None:
        yield start
    else:
        curr = start
        while curr <= end:
            yield curr
            curr += step


class CalendarDay:

    def __init__(self, d, on_requested_interval = True):
        self.date = d
        now = date.today()
        self.in_past = d < now
        self.today = d == now
        self.events = []
        self.on_requested_interval = on_requested_interval

        self.events_by_category = {}

    def is_in_past(self):
        return self.in_past
    def is_today(self):
        return self.today

    def add_event(self, event):
        self.events.append(event)
        if not event.category.name in self.events_by_category:
            self.events_by_category[event.category.name] = []
        self.events_by_category[event.category.name].append(event)


class CalendarList:

    def __init__(self, firstdate, lastdate, filter):
        self.firstdate = firstdate
        self.lastdate = lastdate
        self.now = date.today()
        self.filter = filter

        # start the first day of the first week
        self.c_firstdate = firstdate + timedelta(days=-firstdate.weekday())
        # end the last day of the last week
        self.c_lastdate = lastdate + timedelta(days=6-lastdate.weekday())


        # create a list of CalendarDays
        self.create_calendar_days()

        # fill CalendarDays with events
        self.fill_calendar_days()


    def today_in_calendar(self):
        return self.firstdate <= self.now and self.lastdate >= self.now

    def all_in_past(self):
        return self.lastdate < self.now

    def fill_calendar_days(self):
        if self.filter is None:
            qs = Event.objects()
        else:
            qs = self.filter.qs
        self.events = qs.filter(start_day__lte=self.c_lastdate, start_day__gte=self.c_firstdate).order_by("start_day", "start_time")

        for e in self.events:
            for d in daterange(e.start_day, e.end_day):
                if d.__str__() in self.calendar_days:
                    self.calendar_days[d.__str__()].add_event(e)


    def create_calendar_days(self):
        # create daylist
        self.calendar_days = {}
        for d in daterange(self.c_firstdate, self.c_lastdate):
            self.calendar_days[d.strftime("%Y-%m-%d")] = CalendarDay(d, d >= self.firstdate and d <= self.lastdate)


    def is_single_week(self):
        return hasattr(self, "week")

    
    def is_full_month(self):
        return hasattr(self, "month")


    def calendar_days_list(self):
        return list(self.calendar_days.values())

class CalendarMonth(CalendarList):

    def __init__(self, year, month, filter):
        self.year = year
        self.month = month
        r = calendar.monthrange(year, month)

        first = date(year, month, r[0])
        last = date(year, month, r[1])

        super().__init__(first, last, filter)

    def get_month_name(self):
        return self.firstdate.strftime("%B")

    def next_month(self):
        return self.lastdate + timedelta(days=7)

    def previous_month(self):
        return self.firstdate + timedelta(days=-7)


class CalendarWeek(CalendarList):

    def __init__(self, year, week, filter):
        self.year = year
        self.week = week

        first = date.fromisocalendar(self.year, self.week, 1)
        last = date.fromisocalendar(self.year, self.week, 7)

        super().__init__(first, last, filter)

    def next_week(self):
        return self.firstdate + timedelta(days=7)

    def previous_week(self):
        return self.firstdate + timedelta(days=-7)


class EventFilter(django_filters.FilterSet):
    tags = django_filters.MultipleChoiceFilter(choices=[(t, t) for t in Event.get_all_tags()], lookup_expr='icontains', field_name="tags")
    category = django_filters.ModelMultipleChoiceFilter(field_name="category__id", to_field_name='id', queryset=Category.objects.all())
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if len(args) > 0:
            self.url = EventFilter.build_get_url(args[0])
        else:
            self.url = ""


    class Meta:
        model = Event
        fields = ["category", "tags"]
        field_labels = { 'category': "Catégories", "tags": "Étiquettes" }

    def get_url(self):
        return self.url

    def build_get_url(get, first = "?"):
        result = ""
        for p in get:
            if p in ["category", "tags"]:
                for v in get.getlist(p):
                    result += first if len(result) == 0 else "&"
                    result += str(p) + "=" + str(v)
        return result


def home(request):
    return week_view(request)

def month_view(request, year = None, month = None):
    now = date.today()
    if year is None:
        year = now.year
    if month is None:
        month = now.month

    filtering_url = EventFilter.build_get_url(request.GET)
    filter = EventFilter(request.GET, queryset=Event.objects.all())
    cmonth = CalendarMonth(year, month, filter)
    

    context = {"year": year, "month": cmonth.get_month_name(), "calendar": cmonth, "filter": filter }
    return render(request, 'agenda_culturel/page-month.html', context)


def week_view(request, year = None, week = None):
    now = date.today()
    if year is None:
        year = now.year
    if week is None:
        week = now.isocalendar()[1]

    filtering_url = EventFilter.build_get_url(request.GET)
    filter = EventFilter(request.GET, queryset=Event.objects.all())
    cweek = CalendarWeek(year, week, filter)

    context = {"year": year, "week": week, "calendar": cweek, "filter": filter }
    return render(request, 'agenda_culturel/page-week.html', context)


def day_view(request, year = None, month = None, day = None):
    now = date.today()
    if year is None:
        year = now.year
    if month is None:
        month = now.month
    if day is None:
        day = now.day

    day = date(year, month, day)

    filtering_url = EventFilter.build_get_url(request.GET)
    
    filter = EventFilter(request.GET, Event.objects.all())
    events = filter.qs.filter(start_day__lte=day, start_day__gte=day).order_by("start_day", "start_time")

    context = {"day": day, "events": events, "filter": filter}
    return render(request, 'agenda_culturel/page-day.html', context)


def view_tag(request, t):
    events = Event.objects.filter(tags__contains=[t]).order_by("start_day", "start_time")
    context = {"tag": t, "events": events}
    return render(request, 'agenda_culturel/tag.html', context)

def tag_list(request):
    def remove_accents(input_str):
        nfkd_form = unicodedata.normalize('NFKD', input_str)
        return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

    tags = Event.get_all_tags()    
    context = {"tags": sorted(tags, key=lambda x: remove_accents(x).lower())}
    return render(request, 'agenda_culturel/tags.html', context)


class EventCreateView(CreateView):
    model = Event
    fields = ["title"] # TODO add elements
    template_name_suffix = "_create_form"


class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    fields = ["title"] # TODO add elements


class EventDeleteView(LoginRequiredMixin, DeleteView):
    model = Event
    success_url = reverse_lazy('view_all_events')


class EventDetailView(DetailView):
    model = Event
    template_name = "agenda_culturel/page-event.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        return context


class EventSubmissionFormView(FormView):
    form_class = EventSubmissionModelForm
    template_name = "agenda_culturel/import.html"
    success_url = "/"

    def form_valid(self, form):
        form.save()
        self.create_event(form.cleaned_data)

        return super().form_valid(form)

    def create_event(self, valid_data):
        url = valid_data["url"]
        create_event_from_submission.delay(url)




class EventFilterAdmin(django_filters.FilterSet):
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
    filter = EventFilterAdmin(request.GET, queryset=Event.objects.all())
    paginator = Paginator(filter.qs, 10)
    page = request.GET.get('page')

    try:
        response = paginator.page(page)
    except PageNotAnInteger:
        response = paginator.page(1)
    except EmptyPage:
        response = paginator.page(paginator.num_pages)

    return render(request, 'agenda_culturel/list.html', {'filter': filter, 'paginator_filter': response})
