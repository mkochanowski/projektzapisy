import json

from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.core.cache import cache
from apps.enrollment.courses.models.semester import Semester
from apps.grade.poll.models.poll import Poll
from apps.grade.ticket_create.serializers import SigningRequestsListSerializer
from apps.grade.ticket_create.utils import generate_keys_for_polls, \
    match_signing_requests_with_polls, get_signing_response, mark_poll_used
from apps.users.decorators import employee_required, student_required


@employee_required
def ajax_keys_generate(request):
    generate_keys_for_polls()
    return HttpResponse("OK")


@employee_required
def ajax_keys_progress(request):
    count = cache.get('generated-keys', 0)
    return HttpResponse(str(count))


@student_required
def get_poll_data(request):
    """
    For each poll student is allowed to vote in, responds with its public key
    and information, such as course name, teachers name.
    """
    students_polls = Poll.get_all_polls_for_student(request.user.student)
    response_data = []
    for poll in students_polls:
        poll_data = {
            'key': poll.signingkey.serialize_for_signing_protocol(),
            'poll_info': poll.serialize_for_signing_protocol(),
        }
        response_data.append(poll_data)
    return JsonResponse({
        'poll_data': response_data,
    })


@require_POST
@student_required
def sign_tickets(request):
    """Reads tickets sent by the user, signs them and marks them as already
    used, so user cannot sign them twice. Responds with generated signatures.
    """
    try:
        signing_requests = json.loads(request.body.decode('utf-8'))
    except json.decoder.JSONDecodeError:
        return JsonResponse({
            'error': "Couldn't parse json"
        })

    valid_ser = SigningRequestsListSerializer(data=signing_requests)
    if not valid_ser.is_valid():
        return JsonResponse({
            'error': 'Invalid request'
        })
    try:
        matched_requests = match_signing_requests_with_polls(
            valid_ser.validated_data['signing_requests'], request.user)
    except KeyError:
        return JsonResponse({
            'error': "Couldn't match provided id with poll"
        })

    response = []
    for signing_request, poll in matched_requests:
        signing_response = get_signing_response(request.user, poll, signing_request)
        if signing_response['status'] != 'ERROR':
            mark_poll_used(request.user, poll)
        response.append(signing_response)

    return JsonResponse(response, safe=False)


@student_required
def tickets_generate(request):
    grade = Semester.objects.filter(is_grade_active=True).count() > 0
    if grade:
        polls_lists, general_polls = Poll.get_polls_list(request.user.student)
        data = {'polls': polls_lists, 'grade': grade, 'general_polls': general_polls}
        return render(request, 'grade/ticket_create/tickets_generate.html', data)
    else:
        messages.error(request, "Ocena zajęć jest w tej chwili zamknięta; nie można pobrać biletów")
        return render(request, 'grade/ticket_create/tickets_generate.html', {'grade': grade})


@employee_required
def keys_generate(request):
    data = {}
    data['keys_to_create'] = Poll.count_current_semester_polls_without_keys()
    return render(request, 'grade/ticket_create/keys_generate.html', data)
