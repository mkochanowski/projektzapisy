from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt

from apps.notifications.models import Notification
from .forms import NotificationFormset

GENERIC_ERROR = 'Wystąpił błąd podczas wysyłania powiadomień!'


@require_POST
@login_required
def save(request):

    formset = NotificationFormset(request.POST)

    if formset.is_valid():
        formset.save()
        messages.success(request, 'Zmieniono ustawienia powiadomień')

    else:
        messages.error(request, 'Wystąpił błąd przy zapisie zmian ustawień')

    return redirect('my-profile')


@staff_member_required
def index(request):
    from datetime import date

    year = date.today().year

    return render(request, 'notifications/index.html', {'year': year})


@require_POST
@staff_member_required
def vote_start(request):
    from apps.offer.vote.models.system_state import SystemState
    try:
        try:
            year = int(request.POST['year'])
        except ValueError:
            raise ValueError('Błędny rok akademicki')

        which = request.POST['which']
        if which not in ['main', 'winter', 'summer']:
            raise ValueError('Błędny rodzaj głosowania')

        state = SystemState.get_state(year)

        if which == 'main':
            end_of_vote_date = state.vote_end
        elif which == 'winter':
            end_of_vote_date = state.winter_correction_end
        else:
            end_of_vote_date = state.summer_correction_end

        Notification.send_notifications('vote-start', {'end_of_vote_date': end_of_vote_date})

        messages.success(request, 'Wysłano powiadomienia o rozpoczęciu głosowania!')
    except ValueError as e:
        messages.error(request, str(e))
    except BaseException:
        messages.error(request, GENERIC_ERROR)

    return redirect('notifications:index')


@staff_member_required
def grade_start(request):
    from apps.enrollment.courses.models.semester import Semester
    try:
        semester = Semester.get_current_semester()

        if not semester:
            raise ValueError('Nie można zidentyfikować bieżącego semestru!')

        if not semester.is_grade_active:
            raise ValueError('Ocena zajęć nie jest w tej chwili aktywna!')

        Notification.send_notifications('grade-start')

        messages.success(request, 'Wysłano powiadomienia o rozpoczęciu oceny zajęć')
    except ValueError as e:
        messages.error(request, str(e))
    except BaseException:
        messages.error(request, GENERIC_ERROR)

    return redirect('notifications:index')


@staff_member_required
def enrollment_limit(request):
    from django.conf import settings
    try:
        Notification.send_notifications('enrollment-limit',
                                        {'ECTS_INITIAL_LIMIT': settings.ECTS_INITIAL_LIMIT,
                                         'ECTS_FINAL_LIMIT': settings.ECTS_FINAL_LIMIT})

        messages.success(request, 'Wysłano powiadomienia o zwiększeniu limitu punktów ECTS')
    except BaseException:
        messages.error(request, GENERIC_ERROR)

    return redirect('notifications:index')
