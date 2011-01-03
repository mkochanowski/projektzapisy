# -*- coding: utf8 -*-
from django.db import models

from saved_ticket import SavedTicket

class BaseAnswer( models.Model ):
    saved_ticket = models.ManyToManyField( SavedTicket, verbose_name = 'zapisany bilet' )
    
    class Meta:
        abstract = True
