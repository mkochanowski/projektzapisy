# -*- coding: utf-8 -*-
import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST
from apps.enrollment.courses.models import Classroom, Semester, Course
from apps.schedule.filters import EventFilter, ExamFilter
from apps.schedule.forms import EventForm, TermFormSet, DecisionForm, EventModerationMessageForm, EventMessageForm
from apps.schedule.models import Term, Event, EventModerationMessage, EventMessage
from apps.schedule.utils import EventAdapter
from apps.utils.fullcalendar import FullCalendarView, FullCalendarAdapter

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
        event.author = request.user
        formset = TermFormSet(request.POST or None, instance=event)
        if formset.is_valid():
            event.save()
            formset.save()

            return redirect(event)
    else:
        formset = TermFormSet(data = request.POST or None, instance=Event())


    return TemplateResponse(request, 'schedule/reservation.html', locals())

@login_required
def edit_event(request, id=None):
    is_edit = True

    event = Event.get_event_for_moderation_or_404(id, request.user)
    form = EventForm(data = request.POST or None, instance=event, user=request.user)
    formset = TermFormSet(request.POST or None, instance=event)

    if form.is_valid() and formset.is_valid():
        event = form.save(commit=False)
        if not event.id:
            event.author = request.user
        event.save()
        formset.save()

        messages.success(request, u'Zmieniono zdarzenie')

        return redirect(event)

    return TemplateResponse(request, 'schedule/reservation.html', locals())


def session(request, semester=None):
    exams = ExamFilter(request.GET, queryset=Term.get_exams())

    if semester:
        semester = Semester.get_by_id(semester)
    else:
        semester = Semester.get_current_semester()

    return TemplateResponse(request, 'schedule/session.html', locals())

@login_required
def reservations(request):
    events = EventFilter(request.GET, queryset=Event.get_all_without_courses())
    title = u'Zarządzaj rezerwacjami'
    return TemplateResponse(request, 'schedule/reservations.html', locals())

@login_required
def history(request):
    events = EventFilter(request.GET, queryset=Event.get_for_user(request.user))
    title = u'Moje rezerwacje'
    return TemplateResponse(request, 'schedule/history.html', locals())

@require_POST
def decision(request, id):
    event = Event.get_event_for_moderation_only_or_404(id, request.user)
    form = DecisionForm(request.POST, instance=event)
    if form.is_valid():
        form.save()
        messages.success(request, u'Status wydarzenia został zmieniony')
    else:
        messages.error(request, u'Coś poszło źle')

    return redirect(reverse('events:show', args=[str(event.id)]))

def events(request):
    return TemplateResponse(request, 'schedule/events.html', locals())

@login_required
def event(request, id):
    event = Event.get_event_or_404(id, request.user)
    moderation_messages = EventModerationMessage.get_event_messages(event)
    moderation_form     = EventModerationMessageForm()
    event_messages            = EventMessage.get_event_messages(event)
    messages_form       = EventMessageForm()
    decision_form       = DecisionForm(instance=event)

    return TemplateResponse(request, 'schedule/event.html', locals())

@login_required
@require_POST
def moderation_message(request, id):
    event = Event.get_event_for_moderation_or_404(id, request.user)
    form  = EventModerationMessageForm(request.POST)
    if form.is_valid():
        moderation_message = form.save(commit=False)
        moderation_message.event   = event
        moderation_message.author  = request.user
        moderation_message.save()

        messages.success(request, u"Wiadomość została wysłana")
        messages.info(request, u"Wiadomość została również wysłana emailem")

        return redirect( reverse('events:show', args=[str(event.id)]) )

    raise Http404

@login_required
@require_POST
def message(request, id):
    event = Event.get_event_for_moderation_or_404(id, request.user)
    form  = EventMessageForm(request.POST)
    if form.is_valid():
        message = form.save(commit=False)
        message.event   = event
        message.author  = request.user

        message.save()

        messages.success(request, u"Wiadomość została wysłana")
        messages.info(request, u"Wiadomość została również wysłana emailem")

        return redirect( reverse('events:show', args=[str(event.id)]) )

    raise Http404

@login_required
@require_POST
def change_interested(request, id):
    event = Event.get_event_or_404(id, request.user)
    if request.user in event.interested.all():
        event.interested.remove(request.user)
        messages.success(request, u'Nie obsereujesz już wydarzenia')
    else:
        event.interested.add(request.user)
        messages.success(request, u'Obserwujesz wydarzenie')

        return redirect( event )

    raise Http404


@login_required
@permission_required('schedule.manage_events')
def statistics(request):
    semester_id = request.GET.get('semester_id', None)
    semester    = Semester.get_by_id_or_default(semester_id)

    exams = Course.get_courses_with_exam(semester)

    return TemplateResponse(request, 'schedule/statistics.html', locals())

"""
AJAX views
"""



@login_required
def ajax_get_terms(request, year, month, day):
    time  = datetime.date(int(year), int(month), int(day))
    terms = Classroom.get_terms_in_day(time, ajax=True)
    return HttpResponse(terms, mimetype="application/json")


class ClassroomTermsAjaxView(FullCalendarView):
    model = Term
    adapter = EventAdapter

    def get_queryset(self):
        queryset = super(ClassroomTermsAjaxView, self).get_queryset()
        return queryset.filter(room__slug=self.kwargs['slug'])

class EventsTermsAjaxView(FullCalendarView):
    model = Term
    adapter = EventAdapter

    def get_queryset(self):
        queryset = super(EventsTermsAjaxView, self).get_queryset()
        queryset = queryset.filter(event__type='2', event__visible=True)
        return queryset

