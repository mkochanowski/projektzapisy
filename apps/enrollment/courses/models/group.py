# -*- coding: utf8 -*-

from django.db import models

from course import *
from apps.enrollment.records.models import *
from django.db.models import Count

# w przypadku edycji, poprawić też javascript: Fereol.Enrollment.ScheduleCourseTerm.groupTypes
GROUP_TYPE_CHOICES = [('1', 'wykład'), ('2', 'ćwiczenia'), ('3', 'pracownia'),
        ('4', 'ćwiczenia (grupa zaawansowana)'), ('5', 'ćwiczenio-pracownia'),
        ('6', 'seminarium'), ('7', 'lektorat'), ('8', 'WF'),
        ('9', 'repetytorium'), ('10', 'projekt')]

class Group(models.Model):
    """group for course"""
    course = models.ForeignKey('Course', verbose_name='przedmiot', related_name='groups')
    teacher = models.ForeignKey('users.Employee', null=True, blank=True, verbose_name='prowadzący')
    type    = models.CharField(max_length=1, choices=GROUP_TYPE_CHOICES, verbose_name='typ zajęć')
    limit   = models.PositiveSmallIntegerField(default=0, verbose_name='limit miejsc')
    
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
    
    def number_of_students(self):
        """Returns number of students enrolled to particular group"""
        from apps.enrollment.records.models import Record
        return Record.enrolled.filter(group=self).count()

    @staticmethod
    def numbers_of_students(semester):
        '''
            Returns numbers of students enrolled to all groups in particular
            semester
        '''
        from apps.enrollment.records.models import Record
        raw_counts = Record.enrolled.filter(group__course__semester=semester).\
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
    
    class Meta:
        verbose_name = 'grupa'
        verbose_name_plural = 'grupy'
        app_label = 'courses'

    def __unicode__(self):
        return "%s: %s - %s" % (unicode(self.course.entity.get_short_name()),
                                unicode(self.get_type_display()), 
                                unicode(self.get_teacher_full_name()))
