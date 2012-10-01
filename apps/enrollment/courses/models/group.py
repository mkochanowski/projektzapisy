# -*- coding: utf8 -*-

from django.db import models
from django.db.models import signals
from django.db.models import Count
from django.core.cache import cache as mcache

from course import *

import logging

backup_logger = logging.getLogger('project.backup')

# w przypadku edycji, poprawić też javascript: Fereol.Enrollment.CourseGroup.groupTypes
GROUP_TYPE_CHOICES = [('1', 'wykład'), ('2', 'ćwiczenia'), ('3', 'pracownia'),
        ('5', 'ćwiczenio-pracownia'),
        ('6', 'seminarium'), ('7', 'lektorat'), ('8', 'WF'),
        ('9', 'repetytorium'), ('10', 'projekt')]

GROUP_EXTRA_CHOICES = [('',''),
    ("pierwsze 7 tygodni", "pierwsze 7 tygodni"),
    ("drugie 7 tygodni", "drugie 7 tygodni"),
    ('grupa rezerwowa','grupa rezerwowa'),
    ('grupa licencjacka','grupa licencjacka'),
    ('grupa magisterska','grupa magisterska'),
    ('grupa zaawansowana','grupa zaawansowana'),
    (u'wykład okrojony','wykład okrojony'),
    (u'grupa 1','grupa 1'),
    (u'grupa 2','grupa 2'),
    (u'grupa 3','grupa 3'),
    (u'grupa 4','grupa 4'),
    (u'grupa 5','grupa 5'),]

class Group(models.Model):
    """group for course"""
    course = models.ForeignKey('Course', verbose_name='przedmiot', related_name='groups')
    teacher = models.ForeignKey('users.Employee', null=True, blank=True, verbose_name='prowadzący')
    type    = models.CharField(max_length=2, choices=GROUP_TYPE_CHOICES, verbose_name='typ zajęć')
    limit   = models.PositiveSmallIntegerField(default=0, verbose_name='limit miejsc')
    limit_zamawiane = models.PositiveSmallIntegerField(default=0, verbose_name='miejsca dla zamawianych', help_text='miejsca gwarantowane dla studentów zamawianych')
    extra = models.CharField(max_length=20, choices=GROUP_EXTRA_CHOICES, verbose_name='dodatkowe informacje', default='', blank=True)
    export_usos = models.BooleanField(default=True, verbose_name='czy eksportować do usos?')

    cache_enrolled     = models.PositiveIntegerField(null=True, blank=True, editable=False, verbose_name='Cache: ilość zapisanych studentów')
    cache_enrolled_zam = models.PositiveIntegerField(null=True, blank=True, editable=False, verbose_name='Cache: ilość zapisanych studentów zamawianych')
    cache_queued       = models.PositiveIntegerField(null=True, blank=True, editable=False, verbose_name='Cache: ilość studentów w kolejce')
    disable_update_signal = False

    usos_nr = models.IntegerField(null=True, blank=True, verbose_name=u'Nr grupy w usos', help_text='UWAGA! Nie edytuj tego pola sam!')

    def get_teacher_full_name(self):
        """return teacher's full name of current group"""
        if self.teacher is None:
            return u'(nieznany prowadzący)'
        else:
            return self.teacher.user.get_full_name()
    
    def get_all_terms(self):
        """return all terms of current group""" 
        return self.term.all()

    def get_terms_as_string(self):
      return ",".join(map(lambda x: "%s %s-%s" % (x.get_dayOfWeek_display(), x.start_time.hour, x.end_time.hour), self.term.all()))
    get_terms_as_string.short_description = 'Terminy zajęć'

    @staticmethod
    def get_groups_by_semester(semester):
        """ returns all groups in semester """
        return Group.objects.filter(course__semester=semester). \
            select_related('teacher', 'teacher__user', 'course',
            'course__type', 'course__entity', 'course__semester').all()

    @staticmethod
    def get_groups_by_semester_opt(semester):
        """ returns all groups in semester """
        return Group.objects.filter(course__semester=semester). \
            select_related('teacher', 'teacher__user', 'course',
                'course__type', 'course__entity', 'course__semester').all()

    def get_group_limit(self):
        """return maximal amount of participants"""
        return self.limit
    
    def limit_non_zamawiane(self):
        return self.limit - self.limit_zamawiane

    def available_only_for_zamawiane(self, dont_use_cache=False):
        return (self.limit_zamawiane > 0 and
            self.get_count_of_enrolled_non_zamawiane(dont_use_cache=
            dont_use_cache) >= self.limit_non_zamawiane())

    def get_count_of_enrolled(self, dont_use_cache=False):
        from apps.enrollment.records.models import Record
        if dont_use_cache:
            return Record.enrolled.filter(group=self).count()
        self.update_students_counts_if_empty()
        return self.cache_enrolled

    def get_count_of_enrolled_zamawiane(self, dont_use_cache=False):
        from apps.enrollment.records.models import Record
        from apps.users.models import StudiaZamawiane
        if dont_use_cache:
            enrolled_zam = Record.enrolled.filter(group=self).values_list(
                'student', flat=True)
            return StudiaZamawiane.objects.filter(student__in=\
                enrolled_zam).count()
        self.update_students_counts_if_empty()
        return self.cache_enrolled_zam

    def get_count_of_enrolled_non_zamawiane(self, dont_use_cache=False):
        return self.get_count_of_enrolled(dont_use_cache=dont_use_cache) - \
            self.get_count_of_enrolled_zamawiane(dont_use_cache=dont_use_cache)

    def get_count_of_queued(self, dont_use_cache=False):
        from apps.enrollment.records.models import Queue
        if dont_use_cache:
            return Queue.queued.filter(group=self).count()
        self.update_students_counts_if_empty()
        return self.cache_queued

    def update_students_counts_if_empty(self):
        if (self.cache_enrolled is None) or (self.cache_enrolled_zam is None) \
            or (self.cache_queued is None):
            self.update_students_counts()

    def update_students_counts(self):
        self.cache_queued = self.get_count_of_queued(dont_use_cache=True)
        self.cache_enrolled_zam = self.get_count_of_enrolled_zamawiane(
            dont_use_cache=True)
        self.cache_enrolled = self.get_count_of_enrolled(dont_use_cache=True)
        Group.disable_update_signal = True
        self.save()
        Group.disable_update_signal = False

    def course_slug(self):
        return self.course.slug

    @staticmethod
    def teacher_in_present(employees, semester):
        teachers = Group.objects.filter(course__semester = semester).distinct().values_list('teacher__pk', flat=True)

        for employee in employees:
            employee.teacher = employee.pk in teachers

        return employees

    def serialize_for_ajax(self, enrolled, queued, pinned, queue_priorities,
        student=None, employee=None, user=None):
        """ Dumps this group state to form readable by JavaScript """
        from django.core.urlresolvers import reverse

        zamawiany = user and user.get_profile().is_zamawiany
        data = {
            'id': self.pk,
            'type': int(self.type),
            'course': self.course_id,

            'url': reverse('records-group', args=[self.pk]),
            'teacher_name': self.teacher and self.teacher.user.get_full_name() \
                or 'nieznany prowadzący',
            'teacher_url': self.teacher and reverse('employee-profile', args= \
                [self.teacher.user.id]) or '',

            'is_teacher': False if (employee is None or self.teacher is None) \
                else self.teacher.id == employee.id,
            'is_enrolled': self.id in enrolled,
            'is_queued': self.id in queued,
            'is_pinned': self.id in pinned,

            'limit': self.limit,
            'unavailable_limit': 0 if zamawiany else self.limit_zamawiane,
            'enrolled_count': self.get_count_of_enrolled(),
            'unavailable_enrolled_count': 0 if zamawiany else \
                min(self.get_count_of_enrolled_zamawiane(),
                    self.limit_zamawiane),
            'queued_count': self.get_count_of_queued(),
            'queue_priority': queue_priorities.get(self.pk,-1)
        }
        
        return data

    def enrollment_are_open(self):
        semester = self.course.semester

        return True

    class Meta:
        verbose_name = 'grupa'
        verbose_name_plural = 'grupy'
        app_label = 'courses'

    @staticmethod
    def get_all_in_semester(semester):
        return Group.objects.filter(course__semester=semester).\
                    select_related('course', 'course__semester', 'course__entity', 'teacher', 'teacher__user').order_by('course__name')

    def __unicode__(self):
        return "%s: %s - %s" % (unicode(self.course.entity.get_short_name()),
                                unicode(self.get_type_display()), 
                                unicode(self.get_teacher_full_name()))

def log_add_group(sender, instance, created, **kwargs):
    if Group.disable_update_signal:
        return
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
    if Group.disable_update_signal:
        return
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

def recache(sender, **kwargs):
    if Group.disable_update_signal:
        return
    mcache.clear()

    
signals.post_save.connect(recache, sender=Group)        
signals.post_delete.connect(recache, sender=Group)	
