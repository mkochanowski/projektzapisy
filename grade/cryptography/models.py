# -*- coding: utf8 -*-
from django.db                  import models
from enrollment.subjects.models import Group, \
                                       Subject

class GroupsConnection( models.Model ):
    subject         = models.ForeignKey(      Subject,
                                              verbose_name = 'przedmiot' )
    groups          = models.ManyToManyField( Group,
                                               verbose_name = 'grupy')
    full_connection = models.ForeignKey(      'self',
                                              verbose_name = 'pełne połączenie', 
                                              null         = True, 
                                              blank        = True )
    name            = models.CharField(       verbose_name = 'nazwa',
                                              max_length   = 100 )

    def save( self, *args, **kwargs ):
        super(GroupsConnection, self).save( *args, **kwargs )
        name = self.subject.name + " "
        for group in self.groups.all():
            name += "\n\t" + group.get_type_display() + \
                    " (" + group.get_teacher_full_name() + ")"
        self.name = name
        super(GroupsConnection, self).save( *args, **kwargs )
        
    def __unicode__(self):
        return unicode(self.name)
    
    class Meta:
        verbose_name        = 'powiązanie grup'
        verbose_name_plural = 'powiązania grup'
        app_label           = 'cryptography'
        
class PublicKey( models.Model ):
    subjects_group = models.ForeignKey( GroupsConnection,
                                        verbose_name = 'powiązanie grup' )
    public_key_PEM = models.TextField(  verbose_name = 'klucz' )
    
    def __unicode__(self):
        return u"Klucz publiczny: " + unicode(self.subjects_group)
    
    class Meta:
        verbose_name        = 'klucz publiczny'
        verbose_name_plural = 'klucze publiczne'
        app_label           = 'cryptography'

class PrivateKey( models.Model ):
    subjects_group = models.ForeignKey( GroupsConnection,
                                        verbose_name = 'powiązanie grup' )
    private_key_PEM = models.TextField( verbose_name = 'klucz prywatny' )

    def __unicode__(self):
        return u"Klucz przywatny: " + unicode(self.subjects_group)

    class Meta:
        verbose_name        = 'klucz prywatny'
        verbose_name_plural = 'klucze prywatne'
        app_label           = 'cryptography'
