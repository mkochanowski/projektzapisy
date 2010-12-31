# -*- coding: utf8 -*-
from django.db import models

class BaseQuestion( models.Model ):
    content = models.CharField( max_length = 250, verbose_name = 'treść' )
    
    class Meta:
        abstract = True
        
    def __unicode__( self ):
        return unicode( self.content )
