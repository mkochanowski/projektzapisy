# -*- coding: utf8 -*-
from django.db                  import models
from users.models               import Student
from enrollment.subjects.models import Group, \
                                       Subject, \
                                       Semester
        
class PublicKey( models.Model ):
    group = models.ForeignKey( Group, verbose_name = 'grupa' )
    public_key = models.TextField(  verbose_name = 'klucz' )
    
    def __unicode__(self):
        return u"Klucz publiczny: " + unicode(self.group)
    
    class Meta:
        verbose_name        = 'klucz publiczny'
        verbose_name_plural = 'klucze publiczne'
        app_label           = 'ticket_create'

class PrivateKey( models.Model ):
    group = models.ForeignKey( Group, verbose_name = 'grupa' )
    private_key = models.TextField( verbose_name = 'klucz prywatny' )

    def __unicode__(self):
        return u"Klucz przywatny: " + unicode(self.group)

    class Meta:
        verbose_name        = 'klucz prywatny'
        verbose_name_plural = 'klucze prywatne'
        app_label           = 'ticket_create'
        
class UsedTicketStamp( models.Model ):
    student           = models.ForeignKey( Student,
                                           verbose_name = "student" )
    group = models.ForeignKey( Group,
                                           verbose_name = "grupa" )
    # semester          = models.ForeignKey( Semester,
    #                                        verbose_name = "semestr" ) do dodania niebawem

    def __unicode__(self):
        return unicode(self.student)+ " " + unicode(self.group) # + " " + unicode(self.semester)
    
    class Meta:
        verbose_name        = 'wykorzystany bilet'
        verbose_name_plural = 'wykorzystane bilety'
        app_label           = 'ticket_create'
