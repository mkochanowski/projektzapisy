# -*- coding: utf8 -*-
from django.db                import models
from fereol.grade.poll.models import Poll

from Crypto.PublicKey         import RSA

class PrivateKey( models.Model ):
    poll        = models.ForeignKey( Poll, verbose_name = 'ankieta' )
    private_key = models.TextField(  verbose_name = 'klucz prywatny' )

    class Meta:
        verbose_name        = 'klucz prywatny'
        verbose_name_plural = 'klucze prywatne'
        app_label           = 'ticket_create'
        
    def __unicode__( self ):
        return u"Klucz prywatny: " + unicode( self.poll )
        
    def sign_ticket( self, ticket ):
        RSAImpl = RSA.RSAImplementation()
        key     = RSAImpl.ImportKey( self.private_key )
        return key.sign( ticket, 0 )
        
    def verify_signature( self, ticket, signed_ticket ):
        RSAImpl = RSA.RSAImplementation()
        key     = RSAImpl.ImportKey( self.private_key )
        return key.verify( ticket, signed_ticket )

