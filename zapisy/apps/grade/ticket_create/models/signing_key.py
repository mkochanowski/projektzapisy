from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15

from subprocess import getstatusoutput

from apps.enrollment.courses.models.semester import Semester
from apps.users.models import Student

from django.db import models
from django.apps import apps

from typing import Dict


class SigningKey(models.Model):
    '''RSA private key, encoded in PEM format.
    Due to nature of RSA, this key also holds its public part.
    '''
    poll = models.OneToOneField('poll.Poll', verbose_name='ankieta', on_delete=models.CASCADE)
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
