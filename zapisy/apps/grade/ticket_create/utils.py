from typing import Tuple, List, Dict
from string import whitespace
from subprocess import getstatusoutput

from Crypto.PublicKey import RSA
from Crypto.Random.random import getrandbits, \
    randint

from django.utils.safestring import SafeText
from django.contrib.auth.models import User

from apps.enrollment.courses.models.semester import Semester

from apps.grade.poll.models import Poll
from apps.users.models import Student
from apps.grade.ticket_create.exceptions import InvalidPollException, TicketUsed
from apps.grade.ticket_create.models import SigningKey, UsedTicketStamp
from functools import cmp_to_key

KEY_BITS = 1024
SEPARATOR = '----------------------------------'


def flatten(x):
    result = []
    for el in x:
        if isinstance(el, list):
            if hasattr(el, "__iter__") and not isinstance(el, str):
                result.extend(flatten(el))
            else:
                result.append(el)
        else:
            result.append(el)

    return result


def cmp(x, y):
    if x < y:
        return -1
    if x == y:
        return 0
    return 1


def poll_cmp(poll1, poll2):
    if poll1.group:
        if poll2.group:
            c = cmp(poll1.group.course.name, poll2.group.course.name)
            if c == 0:
                c = cmp(poll1.group.type, poll2.group.type)
                if c == 0:
                    if poll1.studies_type:
                        if poll2.studies_type:
                            c = cmp(poll1.studies_type, poll2.studies_type)
                            if c == 0:
                                return cmp(poll1.title, poll2.title)
                            else:
                                return c
                        else:
                            return 1
                    else:
                        if poll2.studies_type:
                            return -1
                        else:
                            return cmp(poll1.title, poll2.title)
                else:
                    return c
            else:
                return c
        else:
            return 1
    else:
        if poll2.group:
            return -1
        else:
            if poll1.studies_type:
                if poll2.studies_type:
                    c = cmp(poll1.studies_type, poll2.studies_type)
                    if c == 0:
                        return cmp(poll1.title, poll2.title)
                    else:
                        return c
                else:
                    return 1
            else:
                if poll2.studies_type:
                    return -1
                else:
                    return cmp(poll1.title, poll2.title)


def generate_keys_for_polls(semester: Semester = None):
    if not semester:
        semester = Semester.get_current_semester()
    poll_list = Poll.get_polls_without_keys(semester)
    for poll in poll_list:
        pem_rsa_key = SigningKey.generate_rsa_key()
        key = SigningKey(poll=poll, private_key=pem_rsa_key)
        key.save()


def group_polls_by_course(poll_list):
    if poll_list == []:
        return []

    poll_list.sort(key=cmp_to_key(poll_cmp))

    res = []
    act_polls = []
    act_group = poll_list[0].group

    for poll in poll_list:
        if not act_group:
            if not poll.group:
                act_polls.append(poll)
            else:
                act_group = poll.group
                res.append(act_polls)
                act_polls = [poll]
        else:
            if poll.group:
                if act_group.course == poll.group.course:
                    act_polls.append(poll)
                else:
                    act_group = poll.group
                    res.append(act_polls)
                    act_polls = [poll]
            else:
                act_group = poll.group
                res.append(act_polls)
                act_polls = [poll]

    res.append(act_polls)

    return res


def get_pubkey_as_dict(poll):
    key = RSA.importKey(SigningKey.objects.get(poll=poll).private_key)
    return {
        'n': str(key.n),
        'e': str(key.e),
    }


def check_poll_visiblity(user, poll):
    """Checks, whether user is a student entitled to the poll.

    Raises:
        InvalidPollException: If the user in question is not entitled to the
            poll.
        Student.DoesNotExist: If the user in question is not a student.
    """
    if not poll.is_student_entitled_to_poll(user.student):
        raise InvalidPollException


def check_ticket_not_signed(user, poll):
    """Checks, if the user is a student with a yet unused ticket for the poll.

    Raises:
        TicketUsed: If the user has already used the ticket for the poll.
        Student.DoesNotExist: If the user in question is not a student.
    """
    u = UsedTicketStamp.objects.filter(student=user.student, poll=poll)
    if u:
        raise TicketUsed


def mark_poll_used(user, poll):
    """Saves the user's stamp for the poll.

    Raises:
        Student.DoesNotExist: If the user in question is not a student.
    """
    u = UsedTicketStamp(student=user.student,
                        poll=poll)
    u.save()


def ticket_check_and_sign(user, poll, ticket):
    check_poll_visiblity(user, poll)
    check_ticket_not_signed(user, poll)
    key = SigningKey.objects.get(poll=poll)
    signed = key.sign_ticket(ticket)
    return signed


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
    try:
        signed_ticket = ticket_check_and_sign(user, poll, signing_request['ticket'])
        error_msg = None
    except InvalidPollException:
        error_msg = "Nie jesteś przypisany do tej ankiety"
    except TicketUsed:
        error_msg = "Bilet już pobrano"

    if error_msg:
        return {
            'status': 'ERROR',
            'message': error_msg,
            'id': signing_request['id'],
        }
    else:
        return {
            'status': 'OK',
            'id': signing_request['id'],
            'signature': str(signed_ticket),
        }


def match_signing_requests_with_polls(signing_requests, user):
    """For each signing request, matches it with poll corresponding to provided id, checking
    if ticket for this poll wasn't already signed.

    Raises:
        KeyError: When there is not match between signing request and students polls.
    """
    matched_requests = []
    student_polls = Poll.get_all_polls_for_student_as_dict(user.student)
    for req in signing_requests:
        poll = student_polls[req['id']]

        if req['id'] == poll.pk:
            try:
                check_ticket_not_signed(user, poll)
                matched_requests.append((req, poll))
            except TicketUsed:
                pass
    return matched_requests


def validate_signing_request(signing_request: Dict) -> bool:
    """Checks if values provided in signing request are correct.

    Returns:
        True or False
    """
    try:
        if 'id' not in signing_request or 'ticket' not in signing_request:
            return False
        ticket_as_int = int(signing_request['ticket'])
        if ticket_as_int < 0 or ticket_as_int.bit_length() > KEY_BITS:
            return False
        return True
    except (ValueError, TypeError):
        return False


def get_poll_info_as_dict(poll: Poll):
    res = {}
    res['title'] = poll.title
    if poll.group is not None:
        res['course_name'] = poll.group.course.name
        res['type'] = poll.group.get_type_display()
        res['teacher_name'] = poll.group.get_teacher_full_name()
    if poll.studies_type:
        res['studies_type'] = poll.studies_type

    res['id'] = poll.pk

    return res


def from_plaintext(tickets_plaintext: str) -> List[Tuple[int, int, int]]:
    """Parses plaintext tickets provided by user.

    Returns:
        List of (id, ticket, signature).
    """
    res = []
    pre_tickets = tickets_plaintext.split(SEPARATOR)

    if pre_tickets[-1].strip() == '':
        pre_tickets = pre_tickets[:-1]

    for ticket_plaintext in pre_tickets:
        ticket_plaintext = ticket_plaintext.split()
        id_idx = ticket_plaintext.index('id:')
        id_ = ticket_plaintext[id_idx + 1]
        ticket = ticket_plaintext[id_idx + 2]
        signature = ticket_plaintext[id_idx + 3]
        res.append((int(id_), int(ticket), int(signature)))

    return res
