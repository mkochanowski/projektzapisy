import json
from functools import reduce

from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.contrib.auth import authenticate
from django.utils.safestring import SafeText

from apps.grade.ticket_create.models.student_graded import StudentGraded
from apps.users.models import BaseUser
from apps.enrollment.courses.models.semester import Semester
from apps.grade.poll.models.poll import Poll
from apps.grade.ticket_create.utils import generate_keys_for_polls, generate_keys, group_polls_by_course, \
    secure_signer, get_valid_tickets, to_plaintext, secure_signer_without_save, \
    secure_mark, validate_tickets, get_poll_info_as_dict, get_pubkey_as_dict, \
    match_signing_requests_with_polls
from apps.grade.ticket_create.models import PublicKey
from apps.grade.ticket_create.forms import ContactForm, PollCombineForm
from apps.users.decorators import employee_required, student_required


# KEYS generate:

@employee_required
def ajax_keys_generate(request):
    generate_keys_for_polls()
    return HttpResponse("OK")


@employee_required
def ajax_keys_progress(request):
    count = cache.get('generated-keys', 0)
    return HttpResponse(str(count))


@student_required
def ajax_get_rsa_keys_step1(request):
    """
    For each poll student is allowed to vote in, responds with its public key
    and information, such as course name, teachers name.
    """
    if request.method != 'POST':
        return HttpResponse('Wrong request')

    students_polls = Poll.get_all_polls_for_student(request.user.student)
    response_data = []
    for poll in students_polls:
        poll_data = {
            'key': get_pubkey_as_dict(poll),
            'poll_info': get_poll_info_as_dict(poll),
        }
        response_data.append(poll_data)
    return JsonResponse(response_data, safe=False)


@student_required
def ajax_get_rsa_keys_step2(request):
    """
    Reads tickets sent by the user, signs them and marks them as already
    used, so user cannot sign them twice. Responds with generated signatures.
    """
    if request.method != 'POST':
        return HttpResponse('Wrong request')

    students_polls = Poll.get_all_polls_for_student(request.user.student)
    try:
        signing_requests = json.loads(request.body.decode('utf-8'))
    except json.decoder.JSONDecodeError:
        return HttpResponse('Wrong request')

    signing_requests = validate_tickets(signing_requests)
    matched_requests = match_signing_requests_with_polls(signing_requests, request.user)

    response = []
    for signing_request, poll in matched_requests:
        signed_ticket = secure_signer_without_save(request.user, poll, int(signing_request['ticket']))
        secure_mark(request.user, poll)
        response.append({
            'signature': str(signed_ticket),
            'id': signing_request['id'],
        })

    return JsonResponse(response, safe=False)


@student_required
def connections_choice(request):
    grade = Semester.objects.filter(is_grade_active=True).count() > 0
    students_polls = Poll.get_all_polls_for_student(request.user.student)
    if students_polls:
        semester = students_polls[0].semester
    else:
        semester = None
    groupped_polls = group_polls_by_course(students_polls)
    polls_lists, general_polls = Poll.get_polls_list(request.user.student)
    connected = any(len(x) > 1 for x in groupped_polls)
    if grade:
        data = {'polls': polls_lists, 'grade': grade, 'general_polls': general_polls}
        return render(request, 'grade/ticket_create/connection_choice.html', data)
    else:
        messages.error(request, "Ocena zajęć jest w tej chwili zamknięta; nie można pobrać biletów")
        return render(request, 'grade/ticket_create/connection_choice.html', {'grade': grade})


@csrf_exempt
def keys_generate(request):
    data = {}
    data['keys_to_create'] = Poll.count_polls_without_keys()
    return render(request, 'grade/ticket_create/keys_generate.html', data)
