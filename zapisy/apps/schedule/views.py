# -*- coding: utf-8 -*-
import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST
from apps.enrollment.courses.models import Classroom, Semester
from apps.schedule.filters import EventFilter, ExamFilter
from apps.schedule.forms import EventForm, TermFormSet, DecisionForm
from apps.schedule.models import Term, Event
from apps.utils.fullcalendar import FullCalendarView

__author__ = 'maciek'


def classrooms(request):
    rooms = Classroom.get_in_institute(reservation=True)
    return TemplateResponse(request, 'schedule/classrooms.html', locals())

def classroom(request, slug):
    rooms = Classroom.get_in_institute(reservation=True)
    try:
        room = Classroom.get_by_slug(slug)
    except ObjectDoesNotExist:
        raise Http404

    return TemplateResponse(request, 'schedule/classroom.html', locals())

@login_required
def reservation(request, id=None):
    form = EventForm(data = request.POST or None, user=request.user)
    if form.is_valid():
        event = form.save(commit=False)
        event.set_user(request.user)
        formset = TermFormSet(request.POST or None, instance=event)
        if formset.is_valid():
            event.save()
            formset.save()

            return redirect(event)
    else:
        formset = TermFormSet(instance=Event())


    return TemplateResponse(request, 'schedule/reservation.html', locals())

@login_required
def ajax_get_terms(request, year, month, day):

#    if not request.is_ajax():
#        raise Http404

    time  = datetime.date(int(year), int(month), int(day))
    terms = Classroom.get_terms_in_day(time, ajax=True)
    return HttpResponse(terms, mimetype="application/json")

def session(request, semester=None):
    exams = ExamFilter(request.GET, queryset=Term.get_exams())
    return TemplateResponse(request, 'schedule/session.html', locals())

@login_required
def reservations(request):
    events = EventFilter(request.GET, queryset=Event.get_from_request())
    return TemplateResponse(request, 'schedule/reservations.html', locals())

@login_required
def history(request):
    events = EventFilter(request.GET, queryset=Event.get_for_user(request.user))
    return TemplateResponse(request, 'schedule/history.html', locals())

@require_POST
def decision(request):
    event = Event.objects.get(id=request.POST['eventid'])
    form = DecisionForm(request.POST, instance=event)
    if form.is_valid():
        form.save()
        messages.success(request, u'Status wydarzenia został zmieniony')
    else:
        messages.error(request, u'Coś poszło źle')

    return redirect('events:reservations')

def events(request):
    return TemplateResponse(request, 'schedule/events.html', locals())

def event(request):
    pass


class ClassroomTermsAjaxView(FullCalendarView):
    model = Term

    def get_queryset(self):
        queryset = super(ClassroomTermsAjaxView, self).get_queryset()
        return queryset.filter(room__slug=self.kwargs['slug'])

class EventsTermsAjaxView(FullCalendarView):
    model = Term

    def get_queryset(self):
        queryset = super(EventsTermsAjaxView, self).get_queryset()
        queryset = queryset.filter(event__type='2', event__visible=True)
        return queryset