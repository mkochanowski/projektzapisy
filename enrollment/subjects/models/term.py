# -*- coding: utf8 -*-

from django.db import models
from datetime import time
  
DAYS_OF_WEEK = [( '1', u'poniedziałek' ), ( '2', u'wtorek' ), ( '3', u'środa' ), ( '4', u'czwartek'), ( '5', u'piątek'), ( '6', u'sobota'), ( '7', u'niedziela')]

HOURS = [(str(hour), "%s.00" % hour) for hour in range(8, 23)] 
  
class Term( models.Model ):
    """terms of groups"""
    dayOfWeek = models.CharField( max_length = 1, choices = DAYS_OF_WEEK, verbose_name = 'dzień tygodnia') 
    hourFrom = models.CharField(max_length = 2, choices = HOURS, verbose_name = 'od')
    hourTo = models.CharField(max_length = 2, choices = HOURS, verbose_name = 'do')

    def day_in_zero_base(self):
        return int(self.dayOfWeek)-1
    
    def length_in_minutes(self):
        timeFrom = self.time_from()
        timeTo = self.time_to()
        return (timeTo.hour - timeFrom.hour)*60 + (timeTo.minute - timeFrom.minute) 
    
    def time_from_in_minutes(self):
        "Returns number of minutes from start of day (midnight) to term beggining"""
        timeFrom = self.time_from()
        return (timeFrom.hour)*60 + (timeFrom.minute) 

    def time_from(self):
        "Returns hourFrom in time format"""
        return self._convert_string_to_time(self.get_hourFrom_display())
  
    def time_to(self):
        "Returns hourTo in time format"""
        return self._convert_string_to_time(self.get_hourTo_display())

    def _convert_string_to_time(self, str):
        hour, minute = map(lambda x: int(x), str.split('.'))
        return time(hour=hour, minute=minute)

    class Meta:
        verbose_name = 'termin'
        verbose_name_plural = 'terminy'
        app_label = 'subjects'

    def __unicode__(self):
        return "%s (%s-%s)" % (self.get_dayOfWeek_display(), self.get_hourFrom_display(), self.get_hourTo_display())