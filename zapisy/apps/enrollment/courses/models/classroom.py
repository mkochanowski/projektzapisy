# -*- coding: utf-8 -*-
from datetime import time
from django.core.urlresolvers import reverse

from django.db import models
import json
from django.db.models import Q
from autoslug import AutoSlugField

floors = [(0, 'Parter'), (1, 'I piętro'), (2, 'II Piętro'), (3, 'III piętro')]
types = [(0, u'Sala wykładowa'), (1, u'Sala ćwiczeniowa'), (2, u'Pracownia komputerowa - Windows'), (3, u'Pracownia komputerowa - Linux')]



class Classroom( models.Model ):
    """classroom in institute"""
    type = models.IntegerField(choices=types, default=1, verbose_name='typ')
    description = models.TextField(null=True, blank=True, verbose_name='opis')
    number = models.CharField( max_length = 20, verbose_name = 'numer sali' )
    order = models.IntegerField(null=True, blank=True)
    building = models.CharField( max_length = 75, verbose_name = 'budynek', blank=True, default='' )
    capacity = models.PositiveSmallIntegerField(default=0, verbose_name='liczba miejsc')
    floor = models.IntegerField(choices=floors, null=True, blank=True)
    can_reserve = models.BooleanField(default=False)
    slug =  AutoSlugField(populate_from='number', unique_with='number')

    
    class Meta:
        verbose_name = 'sala'
        verbose_name_plural = 'sale'
        app_label = 'courses'
        ordering = ['order', 'floor', 'number']

    def get_absolute_url(self):
        return reverse('events:classroom', args=[self.slug])
    
    def __unicode__(self):
        return self.number + ' ('+str(self.capacity)+')'

    @classmethod
    def get_by_number(cls, number):
        return cls.objects.get(number=number)

    @classmethod
    def get_by_id(cls, id):
        return cls.objects.get(id=id)

    @classmethod
    def get_by_slug(cls, slug):
        return cls.objects.get(slug=slug)


    @classmethod
    def get_terms_in_day(cls, date, ajax=False):
        from apps.schedule.models import Term, SpecialReservation
        from apps.enrollment.courses.models import Semester, DAYS_OF_WEEK

        rooms = cls.get_in_institute(reservation=True)
        terms = Term.objects.filter(day=date, room__in=rooms, event__status='1').select_related('room', 'event')
        special_reservations = SpecialReservation.objects.filter(semester=Semester.get_current_semester(),
                                                                 dayOfWeek=str(date.weekday()+1),
                                                                 classroom__in=rooms).select_related('classroom')
        print "This is a test string ", len(special_reservations)
        if not ajax:
            return rooms

        result = {}

        for room in rooms:

            if room.number not in result:
                result[room.number] = {'id'       : room.id,
                                       'number'  : room.number,
                                       'capacity': room.capacity,
                                       'type': room.get_type_display(),
                                       'description': room.description,
                                       'title': room.number,
                                       'terms': []}

        for term in terms:
            result[term.room.number]['terms'].append({'begin': ':'.join(str(term.start).split(':')[:2]),
                                         'end': ':'.join(str(term.end).split(':')[:2]),
                                         'title': term.event.title})

        for reservation in special_reservations:
            result[reservation.classroom.number]['terms'].append(
                {'begin': ':'.join(str(reservation.start_time).split(':')[:2]),
                 'end': ':'.join(str(reservation.end_time).split(':')[:2]),
                 'title': reservation.title
                 })



        return json.dumps(result)


    @classmethod
    def get_in_institute(cls, reservation=False):
        rooms = cls.objects.all()

        if reservation:
            rooms = rooms.filter(can_reserve=True).order_by('floor', 'number')

        return rooms
