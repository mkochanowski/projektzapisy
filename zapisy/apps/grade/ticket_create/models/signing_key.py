import json

from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15

from subprocess import getstatusoutput
from collections import namedtuple

from apps.enrollment.courses.models.semester import Semester
from apps.users.models import Student
from apps.grade.ticket_create.serializers import TicketsListSerializer
from apps.grade.poll.models import Poll

from django.db import models
from django.apps import apps

from typing import Dict, List, Tuple


PollWithTicketId = namedtuple('PollWithTicketId', ['ticket_id', 'poll'])


class SigningKey(models.Model):
    '''RSA private key, encoded in PEM format.
    Due to nature of RSA, this key also holds its public part.
    '''
    poll = models.OneToOneField(Poll, verbose_name='ankieta', on_delete=models.CASCADE)
    private_key = models.TextField(verbose_name='klucz prywatny')
    students = models.ManyToManyField('users.Student', related_name='signingkeys')

    class Meta:
        verbose_name = 'klucz prywatny'
        verbose_name_plural = 'klucze prywatne'
        app_label = 'ticket_create'

    def __str__(self):
        return f'Klucz prywatny: {self.poll}'

    def sign_ticket(self, ticket: int) -> int:
        key = RSA.importKey(self.private_key)
        if ticket >= key.n or ticket <= 0:
            raise ValueError
        signed = pow(ticket, key.d, key.n)
        return signed

    def verify_signature(self, ticket: int, signature: int) -> bool:
        pk = RSA.importKey(self.private_key)
        signature_pow_e = pow(signature, pk.e, pk.n)
        ticket_hash = SHA256.new(str(ticket).encode()).hexdigest()
        ticket_hash_as_int = int(ticket_hash, 16)

        return ticket_hash_as_int == signature_pow_e

    def serialize_for_signing_protocol(self) -> Dict[str, str]:
        '''Extracts public parts of the key, needed for ticket signing protocol'''
        key = RSA.importKey(self.private_key)
        return {
            'n': str(key.n),
            'e': str(key.e),
        }

    def student_used_key(self, student: Student) -> bool:
        '''Checks if student already used this key to sign his ticket'''
        return self.students.filter(pk=student.pk).exists()

    @staticmethod
    def generate_rsa_key() -> str:
        """Generates RSA key, exported in PEM format"""

        key_length = 1024
        RSAkey = RSA.generate(key_length)

        # Converting the resulting keys to strings should be a safe operation
        # as we explicitly specify the PEM format, which is a textual encoding
        # see https://www.dlitz.net/software/pycrypto/api/current/Crypto.PublicKey.RSA._RSAobj-class.html#exportKey
        key = RSAkey.exportKey('PEM').decode(encoding='ascii', errors='strict')
        return key

    @staticmethod
    def parse_raw_tickets(raw_tickets: str) -> Tuple[List[PollWithTicketId], List[Poll]]:
        '''Parses raw json containing tickets.

        Raises:
            JSONDecodeError: when provided string is not in json format.
            ValueError: when there is something wrong with internal ticket format,
                for example, some of the requred fields are not provided, type
                of field is incorrect, there are duplicate ids, or id does not
                exist in database.

        Returns:
            Tuple of (valid_polls, error_polls), where error_polls are list of those
            polls, for which signature was incorrect, and valid_polls is list of named tuples,
            containing two fields, ticket_id and poll, where ticket_id can be used to
            track which ticket has already been used to vote.
        '''
        tickets = json.loads(raw_tickets)
        valid_ser = TicketsListSerializer(data=tickets)
        if not valid_ser.is_valid():
            raise ValueError
        tickets_list = valid_ser.validated_data['tickets']

        tickets_ids = [ticket['id'] for ticket in tickets_list]

        # Make sure there are no duplicate ids
        if len(tickets_ids) != len(set(tickets_ids)):
            raise ValueError

        polls = Poll.objects.filter(pk__in=tickets_ids).select_related('signingkey').order_by('pk')
        # Make sure all provided ids exist in database
        if len(polls) != len(tickets_list):
            raise ValueError
        tickets_list.sort(key=lambda ticket: ticket['id'])

        valid_polls = []
        error_polls = []

        for poll, ticket in zip(polls, tickets_list):
            if poll.signingkey.verify_signature(ticket['ticket'], ticket['signature']):
                valid_polls.append(PollWithTicketId(ticket_id=ticket['ticket'], poll=poll))
            else:
                error_polls.append(poll)

        return valid_polls, error_polls
