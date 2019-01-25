from typing import Tuple, List
from string import whitespace
from subprocess import getstatusoutput

from Crypto.PublicKey import RSA
from Crypto.Random.random import getrandbits, \
    randint

from django.utils.safestring import SafeText

from apps.grade.poll.models import Poll
from apps.grade.ticket_create.exceptions import InvalidPollException, TicketUsed
from apps.grade.ticket_create.models import PublicKey, \
    PrivateKey, \
    UsedTicketStamp
from functools import cmp_to_key
from typing import List

KEY_BITS = 1024


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


def cmp(a, b):
    """
    Since there is no cmp in python 3 documentation suggests this expression to
    emulate the feature
    :param a:
    :param b:
    :return:
    """
    return (a > b) - (b < a)


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


def generate_rsa_key() -> Tuple[str, str]:
    """
        Generates RSA key - that is, a pair (public key, private key)
        both exported in PEM format
    """

    # wersja bezpieczniejsza
    #key_length = 1024
    #RSAkey     = RSA.generate(key_length)

    # wersja szybsza
    # do poprawki: tworzenie i usuwanie pliku test_rsa...
    getstatusoutput('ssh-keygen -b 1024 -t "rsa" -f test_rsa -N "" -q')
    RSAkey = RSA.importKey(open('test_rsa').read())
    getstatusoutput('rm test_rsa*')

    def key_to_str(bin_key):
        return bin_key.decode(encoding='ascii', errors='strict')

    # Converting the resulting keys to strings should be a safe operation
    # as we explicitly specify the PEM format, which is a textual encoding
    # see https://www.dlitz.net/software/pycrypto/api/current/Crypto.PublicKey.RSA._RSAobj-class.html#exportKey
    privateKey = key_to_str(RSAkey.exportKey('PEM'))
    publicKey = key_to_str(RSAkey.publickey().exportKey('PEM'))
    return (publicKey, privateKey)


PollKeys = List[Tuple[Poll, str]]


def save_public_keys(polls_public_keys: PollKeys):
    for (poll, key) in polls_public_keys:
        print(poll)
        pkey = PublicKey(poll=poll,
                         public_key=key)
        pkey.save()


def save_private_keys(polls_private_keys: PollKeys):
    for (poll, key) in polls_private_keys:
        pkey = PrivateKey(poll=poll,
                          private_key=key)
        pkey.save()


def generate_keys_for_polls(semester=None):
    from apps.enrollment.courses.models.semester import Semester
    if not semester:
        semester = Semester.get_current_semester()
    poll_list = Poll.get_polls_without_keys(semester)
    pub_list = []
    priv_list = []
    i = 1
    for el in poll_list:
        (pub, priv) = generate_rsa_key()
        pub_list.append(pub)
        priv_list.append(priv)
        i = i + 1
    save_public_keys(list(zip(poll_list, pub_list)))
    save_private_keys(list(zip(poll_list, priv_list)))
    print(i - 1)
    return


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


def generate_keys(poll_list):
    keys = []

    for poll in poll_list:
        key = RSA.importKey(PublicKey.objects.get(poll=poll).public_key)
        keys.append((str(key.n), str(key.e)))

    return keys


def get_pubkey_as_dict(poll):
    key = RSA.importKey(PublicKey.objects.get(poll=poll).public_key)
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


def ticket_check_and_mark(user, poll):
    check_poll_visiblity(user, poll)
    check_ticket_not_signed(user, poll)
    mark_poll_used(user, poll)


def ticket_check_and_sign(user, poll, ticket):
    check_poll_visiblity(user, poll)
    check_ticket_not_signed(user, poll)
    key = PrivateKey.objects.get(poll=poll)
    signed = key.sign_ticket(ticket)
    mark_poll_used(user, poll)


def ticket_check_and_sign_without_mark(user, poll, ticket):
    check_poll_visiblity(user, poll)
    check_ticket_not_signed(user, poll)
    key = PrivateKey.objects.get(poll=poll)
    signed = key.sign_ticket(ticket)
    return signed


def secure_signer_without_save(user, g, t):
    try:
        return ticket_check_and_sign_without_mark(user, g, t)
    except InvalidPollException:
        return "Nie jesteś przypisany do tej ankiety",
    except TicketUsed:
        return "Bilet już pobrano",
    except ValueError:
        return "Niepoprawny format"


def match_signing_requests_with_polls(signing_requests, user):
    """
    For each signing request, matches it with poll corresponding to provided id, checking
    if ticket for this poll wasn't already signed.
    """
    matched_requests = []
    student_polls = Poll.get_all_polls_for_student(user.student)
    for req in signing_requests:
        for poll in student_polls:
            if req['id'] == poll.pk:
                try:
                    check_ticket_not_signed(user, poll)
                    matched_requests.append((req, poll))
                except TicketUsed:
                    pass
    return matched_requests


def validate_tickets(signing_requests):
    res = []
    for req in signing_requests:
        try:
            ticket_as_int = int(req['ticket'])
            if ticket_as_int < 0 or ticket_as_int.bit_length() > KEY_BITS:
                raise ValueError
            res.append(req)
        except ValueError:
            continue
    return res


def secure_mark(user, poll):
    try:
        return ticket_check_and_mark(user, poll),
    except InvalidPollException:
        return "Nie jesteś przypisany do tej ankiety",
    except TicketUsed:
        return "Bilet już pobrano",


def secure_signer(user, g, t):
    try:
        return ticket_check_and_sign(user, g, t),
    except InvalidPollException:
        return "Nie jesteś przypisany do tej ankiety",
    except TicketUsed:
        return "Bilet już pobrano",


def get_valid_tickets(ticket_list):
    err = []
    val = []
    for group, ticket, st in ticket_list:
        if st == "Nie jesteś przypisany do tej ankiety" or \
           st == "Bilet już pobrano":
            err.append((str(group), st))
        else:
            val.append((group, ticket, st))
    return err, val


def to_plaintext(vtl):
    res = ""
    for p, t, st in vtl:
        res += '[' + p.title + ']'
        if not p.group:
            res += 'Ankieta ogólna &#10;'
        else:
            res += str(p.group.course.name) + " &#10;"
            res += str(p.group.get_type_display()) + ": "
            res += str(p.group.get_teacher_full_name()) + " &#10;"
        if p.studies_type:
            res += 'typ studiów: ' + str(p.studies_type) + " &#10;"

        res += 'id: ' + str(p.pk) + ' &#10;'
        res += str(t) + " &#10;"
        res += str(st) + " &#10;"
        res += "---------------------------------- &#10;"
    return SafeText(str(res))


def get_poll_info_as_dict(poll):
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


# FIXME explanation of ticket parsing code: str(int())
# The list is split into chunks, some of which are empty, and some of which
# contain the tickets we want (e.g. ['123123', '', '', 'somecrap', '321321'])
# The list is iterated until doing int(list[i]) succeeds; at this point
# it's assumed we've found the key. However, we actually want to return
# the tickets as strings, not ints.
# This entire function should be rewritten from scratch
def from_plaintext(tickets_plaintext):
    pre_tickets = tickets_plaintext.split('----------------------------------')
    pre_tickets = [[x] for x in pre_tickets]
    for sign in whitespace:
        pre_tickets = [flatten(
            [x.split(sign) for x in ls]) for ls in pre_tickets]

    convert = False
    ids_tickets_signed = []
    for poll_info in pre_tickets:
        i = 0
        while i < len(poll_info):
            if convert:
                j = i
                id = -1
                t = -1
                st = -1
                while True:
                    try:
                        id = int(poll_info[j])
                        break
                    except BaseException:
                        j += 1

                j += 1
                while True:
                    try:
                        t = str(int(poll_info[j]))
                        break
                    except BaseException:
                        j += 1

                j += 1
                while True:
                    try:
                        st = int(poll_info[j])
                        break
                    except BaseException:
                        j += 1

                i = j + 1
                convert = False
                ids_tickets_signed.append((id, (t, st)))
            elif poll_info[i].startswith('id:'):
                convert = True
            i += 1

    return ids_tickets_signed
