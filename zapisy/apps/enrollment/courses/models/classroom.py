# -*- coding: utf8 -*-

from django.db import models
import json
from django.db.models import Q

class Classroom( models.Model ):
    """classroom in institute"""
    number = models.CharField( max_length = 20, verbose_name = 'numer sali' )
    building = models.CharField( max_length = 75, verbose_name = 'budynek', blank=True, default='' )
    capacity = models.PositiveSmallIntegerField(default=0, verbose_name='liczba miejsc')   
    
    class Meta:
        verbose_name = 'sala'
        verbose_name_plural = 'sale'
        app_label = 'courses'
    
    def __unicode__(self):
        return self.number + ' ('+str(self.capacity)+')'

    @classmethod
    def get_by_number(cls, number):
        return cls.objects.get(number=number)

    @classmethod
    def get_by_id(cls, id):
        return cls.objects.get(id=id)


    @classmethod
    def get_terms_in_day(cls, date, ajax=False):
        rooms = cls.objects.filter(Q(event_terms__day__exact=date)|Q(event_terms__isnull=True))\
            .prefetch_related('event_terms')\
            .select_related('event_terms__event')

        if not ajax:
            return rooms

        result = {}

        for room in rooms:

            if not room.number in result:
                result[room.number] = {'id'       : room.id,
                                       'number'  : room.number,
                                       'capacity': room.capacity,
                                       'title': room.number,
                                       'terms': []}

            for term in room.event_terms.all():
                result[room.number]['terms'].append({'begin': term.start,
                                             'end': term.end,
                                             'title': term.event.title})

        return json.dumps(result)


    @classmethod
    def get_in_institute(cls):
        return cls.objects.all()