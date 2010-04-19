# -*- coding: utf8 -*-

from django.db import models

from subject import *

GROUP_TYPE_CHOICES = [ ( '1', u'wykład' ), ( '2', u'ćwiczenia' ), ( '3', u'pracownia' ) ]

class Group( models.Model ):
    """group for subject"""
    subject = models.ForeignKey('Subject', verbose_name='przedmiot')
    teacher = models.ForeignKey('users.Employee', verbose_name='prowadzący')
    type = models.CharField(max_length=1, choices=GROUP_TYPE_CHOICES, verbose_name='typ zajęć')
    classroom = models.ManyToManyField('Classroom', verbose_name='sala', related_name='grupy')
    term = models.ManyToManyField('Term', verbose_name='termin zajęć', related_name='grupy')
    limit = models.PositiveSmallIntegerField(default=0, verbose_name='limit miejsc')
    
    @staticmethod
    def get_groups_for_subject(slug, group_type):
        """return all groups of type 'group_type' for subject with given 'slug'"""
# write unit test if necesary
        try:
            subject = Subject.objects.get(slug=slug)
            groups = Group.objects.filter(subject=subject).filter(type=group_type)
            return groups
        except Subject.DoesNotExist:
            raise NonSubjectException()
        
    def get_teacher_full_name(self):
        """return teacher's full name of current group"""
        return self.teacher.user.get_full_name()

    def get_all_terms(self):
        """return all terms of current group""" 
        return self.term.all()

    def get_all_classrooms(self):
        """return all classrooms of current group""" 
        return self.classroom.all()

    def get_group_limit(self):
        """return maximal amount of participants"""
        return self.limit

    def subject_slug(self):
        return self.subject.slug

    class Meta:
        verbose_name = 'grupa'
        verbose_name_plural = 'grupy'
        app_label = 'subjects'

    def __unicode__(self):
        return "%s: %s" % (self.subject.name, self.get_type_display())