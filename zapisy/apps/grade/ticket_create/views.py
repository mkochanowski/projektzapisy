import json

from apps.enrollment.courses.models.semester import Semester
from apps.grade.poll.models import Poll
from apps.grade.ticket_create.serializers import SigningRequestsListSerializer
from apps.grade.ticket_create.models import SigningKey
from apps.users.decorators import student_required
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST


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
@transaction.atomic
def sign_tickets(request):
    """Reads tickets sent by the user, signs them and marks them as already
    used, so user cannot sign them twice. Responds with generated signatures.
    """
    try:
        signing_requests = json.loads(request.body.decode('utf-8'))
    except json.decoder.JSONDecodeError:
        return HttpResponseBadRequest("Couldn't parse json")

    valid_ser = SigningRequestsListSerializer(data=signing_requests)
    if not valid_ser.is_valid():
        return HttpResponseBadRequest("Invalid request")
    try:
        matched_requests = SigningKey.match_signing_requests_with_polls(
            valid_ser.validated_data['signing_requests'], request.user)
    except KeyError:
        return HttpResponseBadRequest("Couldn't match provided id with poll")

    response = []
    for signing_request, poll in matched_requests:
        signing_response = SigningKey.get_signing_response(request.user, poll, signing_request)
        if signing_response['status'] != 'ERROR':
            # mark poll used
            poll.signingkey.students.add(request.user.student)
        response.append(signing_response)

    return JsonResponse(response, safe=False)


@student_required
def tickets_generate(request):
    grade = Semester.objects.filter(is_grade_active=True).exists()
    if not grade:
        messages.error(request, "Ocena zajęć jest w tej chwili zamknięta; nie można pobrać biletów")
        return render(request, 'ticket_create/tickets_generate.html', {'grade': grade, 'is_grade_active': grade})
    polls_for_courses, other_polls = Poll.get_polls_courses_and_general(request.user.student)
    data = {'polls': polls_for_courses, 'grade': grade, 'general_polls': other_polls, 'is_grade_active': grade}
    return render(request, 'ticket_create/tickets_generate.html', data)
