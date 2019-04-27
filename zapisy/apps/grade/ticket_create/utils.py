from typing import Dict
from django.contrib.auth.models import User
from apps.grade.poll.models import Poll
from apps.grade.ticket_create.models import SigningKey


def mark_poll_used(user, poll):
    poll.signingkey.students.add(user.student)


def get_signing_response(user: User, poll: Poll, signing_request: Dict) -> Dict:
    """Responds to signing request

    Returns:
        Dictionary with keys:
            'status': 'ERROR'
            'message': <error_msg>
            'id': <signing_request_id>
        when something goes wrong, or
        Dictionary with keys
            'status': 'OK'
            'signature': <ticket_signature>
            'id': <signing_request_id>
    """
    error_msg = None
    if poll.signingkey.student_used_key(user.student):
        error_msg = "Bilet już pobrano"
    elif not poll.is_student_entitled_to_poll(user.student):
        error_msg = "Nie jesteś przypisany do tej ankiety"

    if error_msg:
        return {
            'status': 'ERROR',
            'message': error_msg,
            'id': signing_request['id'],
        }
    key = SigningKey.objects.get(poll=poll)
    signed_ticket = key.sign_ticket(signing_request['ticket'])
    return {
        'status': 'OK',
        'id': signing_request['id'],
        'signature': str(signed_ticket),
    }


def match_signing_requests_with_polls(signing_requests, user):
    """For each signing request, matches it with poll corresponding to provided id, ensuring
    that it will match only the polls user is allowed to vote in.

    Raises:
        KeyError: When there is not match between signing request and students polls.
    """
    matched_requests = []
    student_polls = Poll.get_all_polls_for_student_as_dict(user.student)
    for req in signing_requests:
        poll = student_polls[req['id']]
        matched_requests.append((req, poll))
    return matched_requests
