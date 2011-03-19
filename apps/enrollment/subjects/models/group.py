# -*- coding: utf8 -*-

from django.db import models

from subject import *

from apps.enrollment.records.models import *

GROUP_TYPE_CHOICES = [('1', 'wykład'), ('2', 'ćwiczenia'), ('3', 'pracownia'), ('4', 'ćwiczenia (grupa zaawansowana)'), ('5', 'ćwiczenio-pracownia'), ('6', 'seminarium'), ('7', 'lektorat'), ('8', 'WF')]

class Group(models.Model):
    """group for subject"""
    subject = models.ForeignKey('Subject', verbose_name='przedmiot', related_name='groups')
    teacher = models.ForeignKey('users.Employee', null=True, blank=True, verbose_name='prowadzący')
    type = models.CharField(max_length=1, choices=GROUP_TYPE_CHOICES, verbose_name='typ zajęć')
    limit = models.PositiveSmallIntegerField(default=0, verbose_name='limit miejsc')
    
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

    def subject_slug(self):
        return self.subject.slug
    
    class Meta:
        verbose_name = 'grupa'
        verbose_name_plural = 'grupy'
        app_label = 'subjects'

    def __unicode__(self):
        return "%s: %s - %s" % (self.subject.entity.get_short_name(), self.get_type_display(), self.get_teacher_full_name())
