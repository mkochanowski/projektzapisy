from django.db import models
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256

class PublicKey(models.Model):
    '''Public key of a poll, encoded in PEM format.'''
    poll = models.ForeignKey('poll.Poll', verbose_name='ankieta', on_delete=models.CASCADE)
    public_key = models.TextField(verbose_name='klucz publiczny')

    class Meta:
        verbose_name = 'klucz publiczny'
        verbose_name_plural = 'klucze publiczne'
        app_label = 'ticket_create'

    def __str__(self):
        return "Klucz publiczny: " + str(self.poll)

    def verify_signature(self, ticket: int, signature: int) -> bool:
        pk = RSA.importKey(self.public_key)
        signature_pow_e = pow(signature, pk.e, pk.n)
        ticket_hash = SHA256.new(str(ticket).encode()).hexdigest()
        ticket_hash_as_int = int(ticket_hash, 16)

        return ticket_hash_as_int == signature_pow_e