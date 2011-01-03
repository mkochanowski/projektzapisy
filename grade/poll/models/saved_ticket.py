# -*- coding: utf8 -*-
from django.db import models

from poll import Poll

class SavedTicket( models.Model ):
    ticket   = models.TextField( verbose_name = 'bilet' )
    poll     = models.ForeignKey( Poll, verbose_name = 'ankieta' )
    finished = models.BooleanField( verbose_name = 'czy zakończona' )
    
    class Meta:
        verbose_name_plural = 'zapisane bilety'
        verbose_name        = 'zapisany bilet'
        app_label           = 'poll'
