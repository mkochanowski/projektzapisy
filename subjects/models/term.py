# -*- coding: utf8 -*-

from django.db import models
  
DAYS_OF_WEEK = [( '1', u'poniedziałek' ), ( '2', u'wtorek' ), ( '3', u'środa' ), ( '4', u'czwartek'), ( '5', u'piątek'), ( '6', u'sobota'), ( '7', u'niedziela')]

HOURS = [( '8', '8.00' ), ( '9', '9.00' ), ( '10', '10.00' ), ( '11', '11.00' ), ( '12', '12.00' ), ( '13', '13.00' ), ( '14', '14.00' ), ( '15', '15.00' ), 
         ( '16', '16.00' ), ( '17', '17.00' ), ( '17', '17.00' ), ( '18', '18.00' ), ( '19', '19.00' ), ( '20', '20.00' ), ( '21', '21.00' ), ( '22', '22.00' )]  
  
class Term( models.Model ):
   
    """terms of groups"""
    dayOfWeek = models.CharField( max_length = 1, choices = DAYS_OF_WEEK, verbose_name = 'dzień tygodnia') 
    hourFrom = models.CharField(max_length = 2, choices = HOURS, verbose_name = 'od')
    hourTo = models.CharField(max_length = 2, choices = HOURS, verbose_name = 'do')

    class Meta:
        verbose_name = 'termin'
        verbose_name_plural = 'terminy'
        app_label = 'subjects'

    def __unicode__(self):
        return "%s (od %s do %s)" % (self.get_dayOfWeek_display(), self.get_hourFrom_display(), self.get_hourTo_display())