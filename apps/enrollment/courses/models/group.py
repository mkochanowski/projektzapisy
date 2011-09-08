# -*- coding: utf8 -*-

from django.db import models
from django.db.models import signals
from django.db.models import Count

from course import *

import logging

backup_logger = logging.getLogger('project.backup')

# w przypadku edycji, poprawić też javascript: Fereol.Enrollment.CourseGroup.groupTypes
GROUP_TYPE_CHOICES = [('1', 'wykład'), ('2', 'ćwiczenia'), ('3', 'pracownia'),
        ('5', 'ćwiczenio-pracownia'),
        ('6', 'seminarium'), ('7', 'lektorat'), ('8', 'WF'),
        ('9', 'repetytorium'), ('10', 'projekt')]

GROUP_EXTRA_CHOICES = [('',''),('grupa rezerwowa','grupa rezerwowa'),('grupa licencjacka','grupa licencjacka'),('grupa magisterska','grupa magisterska'),('grupa zaawansowana','grupa zaawansowana'),(u'wykład okrojony','wykład okrojony')]

class Group(models.Model):
    """group for course"""
    course = models.ForeignKey('Course', verbose_name='przedmiot', related_name='groups')
    teacher = models.ForeignKey('users.Employee', null=True, blank=True, verbose_name='prowadzący')
    type    = models.CharField(max_length=1, choices=GROUP_TYPE_CHOICES, verbose_name='typ zajęć')
    limit   = models.PositiveSmallIntegerField(default=0, verbose_name='limit miejsc')
    limit_zamawiane = models.PositiveSmallIntegerField(default=0, verbose_name='miejsca gwarantowane dla studentów zamawianych')
    extra = models.CharField(max_length=20, choices=GROUP_EXTRA_CHOICES, verbose_name='dodatkowe informacje', default='', blank=True)
                 
    def get_teacher_full_name(self):
        """return teacher's full name of current group"""
        if self.teacher is None:
            return u'(nieznany prowadzący)'
        else:
            return self.teacher.user.get_full_name()
    
    def get_all_terms(self):
        """return all terms of current group""" 
        return self.term.all()

    def get_group_limit(self):
        """return maximal amount of participants"""
        return self.limit
    
    def limit_non_zamawiane(self):
        return self.limit - self.limit_zamawiane

    def available_only_for_zamawiane(self):
        return (self.limit_zamawiane > 0 and
            self.number_of_students_non_zamawiane() >=
            self.limit_non_zamawiane())

    def number_of_students(self):
        """Returns number of students enrolled to particular group"""
        from apps.enrollment.records.models import Record
        return Record.enrolled.filter(group=self).count()

    def number_of_students_zamawiane(self):
        '''
            Liczba studentów zapisanych w ramach limitu dla studentów
            zamawianych.
        '''
        from apps.enrollment.records.models import Record
        from apps.users.models import StudiaZamawiane
        enrolled = Record.enrolled.filter(group=self).values_list( \
            'student', flat=True)
        zam = StudiaZamawiane.objects.filter(student__in=enrolled).count()
        if zam > self.limit_zamawiane:
            return self.limit_zamawiane
        else:
            return zam

    def number_of_students_non_zamawiane(self):
        return self.number_of_students() - self.number_of_students_zamawiane()

    def number_of_queued_students(self):
        """Returns number of students queued to particular group"""
        from apps.enrollment.records.models import Queue
        return Queue.queued.filter(group=self).count()

    @staticmethod
    def numbers_of_students(semester, enrolled):
        '''
            Returns numbers of students enrolled to all groups in particular
            semester
        '''
        from apps.enrollment.records.models import Record, Queue
        manager = Record.enrolled if enrolled else Queue.queued
        raw_counts = manager.filter(group__course__semester=semester).\
            values('group__pk').order_by().annotate(Count('group__pk'))
        count_map = {}
        for r in raw_counts:
            count_map[r['group__pk']] = r['group__pk__count']
        return count_map

    def course_slug(self):
        return self.course.slug

    @staticmethod
    def teacher_in_present(employees, semester):
        teachers = Group.objects.filter(course__semester = semester).distinct().values_list('teacher__pk', flat=True)

        for employee in employees:
            employee.teacher = employee.pk in teachers

        return employees

    def serialize_for_ajax(self, enrolled, queued, pinned, queue_priorities,
        student=None):
        """ Dumps this group state to form readable by JavaScript """
        from django.utils import simplejson

        zamawiany = student and student.is_zamawiany()
        data = {
            'id': self.pk,
            'type': int(self.type),

            'is_enrolled': self.id in enrolled,
            'is_queued': self.id in queued,
            'is_pinned': self.id in pinned,

            'limit': self.limit,
            'unavailable_limit': 0 if zamawiany else self.limit_zamawiane,
            'enrolled_count': self.number_of_students(),
            'unavailable_enrolled_count': self.number_of_students_zamawiane(),
            'queued_count': self.number_of_queued_students(),
            'queue_priority': queue_priorities.get(self.pk)
        }
        
        return simplejson.dumps(data);

    class Meta:
        verbose_name = 'grupa'
        verbose_name_plural = 'grupy'
        app_label = 'courses'

    def __unicode__(self):
        return "%s: %s - %s" % (unicode(self.course.entity.get_short_name()),
                                unicode(self.get_type_display()), 
                                unicode(self.get_teacher_full_name()))

def log_add_group(sender, instance, created, **kwargs):
    if created:
        group = instance
        GROUP_TYPE_MAPPING = {'1': 'w', '2': 'c', '3': 'p',
        '4': 'C', '5': 'r',
        '6': 's', '7': 'l', '8': 'l',
        '9': 'w', '10': 'p'}
        kod_grupy = group.id 
        kod_przed_sem = group.course.id
        teacher_name_array = (group.teacher and group.teacher.user.get_full_name() or u"Nieznany prowadzący").split(" ")
	kod_uz = teacher_name_array[0]
	if teacher_name_array[0] != teacher_name_array[-1]:
		kod_uz += " " + teacher_name_array[-1]
        max_osoby = group.limit
        rodzaj_zajec = GROUP_TYPE_MAPPING[group.type]
        zamawiane_bonus = group.limit_zamawiane
        message = '[06] group has been created <%s><%s><%s><%s><%s><%s>' % (kod_grupy,kod_przed_sem,kod_uz.encode('utf-8'),max_osoby,rodzaj_zajec,zamawiane_bonus)
        backup_logger.info(message)

def log_limits_change(sender, instance, **kwargs):
    try:
        group = instance
        old_group = Group.objects.get(id=group.id)
        
        if group.limit != old_group.limit:
            backup_logger.info('[04] limit of group <%s> has changed from <%s> to <%s>' % (group.id, old_group.limit, group.limit))
        if group.limit_zamawiane != old_group.limit_zamawiane:
            backup_logger.info('[05] limit-zamawiane of group <%s> has changed from <%s> to <%s>' % (group.id, old_group.limit_zamawiane, group.limit_zamawiane))
    except Group.DoesNotExist:
        pass
        
def log_delete_group(sender, instance, **kwargs):
    backup_logger.info('[07] group <%s> has been deleted' % instance.id)
    
signals.pre_save.connect(log_limits_change, sender=Group)        
signals.post_save.connect(log_add_group, sender=Group)                               
signals.post_delete.connect(log_delete_group, sender=Group)                               
