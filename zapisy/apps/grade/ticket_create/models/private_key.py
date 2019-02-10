from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15

from django.db import models


class PrivateKey(models.Model):
    poll = models.ForeignKey('poll.Poll', verbose_name='ankieta', on_delete=models.CASCADE)
    private_key = models.TextField(verbose_name='klucz prywatny')

    class Meta:
        verbose_name = 'klucz prywatny'
        verbose_name_plural = 'klucze prywatne'
        app_label = 'ticket_create'

    def __str__(self):
        return f'Klucz prywatny: {self.poll}'

    @staticmethod
    def _int_from_bytes(xbytes: bytes) -> int:
        return int.from_bytes(xbytes, 'big')

    def sign_ticket(self, ticket: int) -> int:
        key = RSA.importKey(self.private_key)
        if ticket >= key.n:
            raise ValueError
        signed = pow(ticket, key.d, key.n)
        return signed
