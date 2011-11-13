# -*- coding: utf8 -*-

from datetime import timedelta, datetime

from django.db import models
from django.template.defaultfilters import slugify
from django.db.models import signals
from django.core.cache import cache as mcache

from apps.enrollment.courses.models.points import PointsOfCourses, PointsOfCourseEntities
from student_options import StudentOptions

import logging
logger = logging.getLogger()

class CourseEntity(models.Model):
    """entity of particular course title"""
    name = models.CharField(max_length=100, verbose_name='nazwa')
    shortName = models.CharField(max_length=30, null=True, verbose_name='skrócona nazwa')
    type = models.ForeignKey('Type', null=True, verbose_name='rodzaj')
    description = models.TextField(verbose_name='opis', default='', blank=True) 
    lectures = models.IntegerField(verbose_name='wykład', default=0)
    exercises = models.IntegerField(verbose_name='ćwiczenia', default=0)
    laboratories = models.IntegerField(verbose_name='pracownia', default=0)
    repetitions = models.IntegerField(verbose_name='Repetytorium', default=0)

    class Meta:
        verbose_name = 'Podstawa przedmiotu'
        verbose_name_plural = 'Podstawy przedmiotów'
        app_label = 'courses'
        ordering = ['name']
        
    def __unicode__(self):
        return '%s' % (self.name, )

    def get_short_name(self):
        if self.shortName is None:
            return self.name
        else:
            return self.shortName

class Related(models.Manager):
    """ Manager for course objects with visible semester """
    def get_query_set(self):
        """ Returns all courses which have marked semester as visible """
        return super(Related, self).get_query_set().select_related('semester', 'type', 'type__classroom')

class VisibleManager(models.Manager):
    """ Manager for course objects with visible semester """
    def get_query_set(self):
        """ Returns all courses which have marked semester as visible """
        return super(VisibleManager, self).get_query_set().filter(semester__visible=True)

class Course( models.Model ):
    """course in offer"""
    entity = models.ForeignKey(CourseEntity, verbose_name='podstawa przedmiotu')
    name = models.CharField(max_length=255, verbose_name='nazwa przedmiotu')
    semester = models.ForeignKey('Semester', null=True, verbose_name='semestr')
    slug = models.SlugField(max_length=255, unique=True, verbose_name='odnośnik', null=True)
    type = models.ForeignKey('Type', verbose_name='rodzaj')
    teachers = models.ManyToManyField('users.Employee', verbose_name='prowadzący', blank=True)
    description = models.TextField(verbose_name='opis', blank=True, default='') 
    lectures = models.IntegerField(verbose_name='wykład')
    repetitions = models.IntegerField(verbose_name='Repetytorium', default=0)
    exercises = models.IntegerField(verbose_name='ćwiczenia')
    laboratories = models.IntegerField(verbose_name='pracownia')
    exercises_laboratories = models.IntegerField(verbose_name='ćw+prac', default=0)
    students_options = models.ManyToManyField('users.Student', verbose_name='opcje studentów', through='StudentOptions')
    requirements = models.ManyToManyField(CourseEntity, verbose_name='wymagania', related_name='+', blank=True)
    web_page = models.URLField( verbose_name = 'Strona WWW przedmiotu',
                                verify_exists= True,
								blank        = True,
                                null         = True )
    english = models.BooleanField(default=False, verbose_name='przedmiot prowadzony w j.angielskim')
    exam = models.BooleanField(verbose_name='egzamin')
    suggested_for_first_year = models.BooleanField(verbose_name='polecany dla pierwszego roku')
    
    # XXX: fix tests (fixtures) to safely remove 'null=True' from semester field
    # and also fix get_semester_name method
    
    objects = Related()
    visible = VisibleManager()
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify('%s %s' % (self.name, self.semester))
            if not self.type:
                self.type = self.entity.type
            if not self.lectures:
                self.lectures = self.entity.lectures
            if not self.exercises:
                self.exercises = self.entity.exercises
            if not self.laboratories:
                self.laboratories = self.entity.laboratories
            if not self.repetitions:
                self.repetitions = self.entity.repetitions
            if not self.description:
                self.description = self.entity.description
        super(Course, self).save(*args, **kwargs)
        
    def is_recording_open_for_student(self, student):
        """ gives the answer to question: is course opened for apps.enrollment for student at the very moment? """
        records_opening = self.semester.records_opening
        records_closing = self.semester.records_closing
        try:
            stud_opt = StudentOptions.get_cached(student, self)
            interval = stud_opt.get_opening_delay_timedelta()
        except StudentOptions.DoesNotExist:
            interval = timedelta(minutes=4320) #TODO: 3 dni -> to powinno chyba wylądować w konfigu

        if records_opening == None:
            return False
        else:
            student_opening = records_opening - student.get_t0_interval()
            if student_opening + interval < datetime.now():
                if records_closing == None:
                    return True
                else:
                    return datetime.now() < records_closing
            else:
                return False

    def get_enrollment_opening_time(self, student):
        """ returns course opening time as datetime object or None if course is opened / was opened """
        records_opening = self.semester.records_opening
        try:
            stud_opt = StudentOptions.get_cached(student, self)
            interval = stud_opt.get_opening_delay_timedelta()
        except StudentOptions.DoesNotExist:
            interval = timedelta(minutes=4320)

        if records_opening == None:
            return False
        else:
            student_opening = records_opening - student.get_t0_interval()
            if student_opening + interval < datetime.now():
                return None
            else:
                return student_opening + interval
        
    def get_semester_name(self):
        """ returns name of semester course is linked to """
        if self.semester is None:
            logger.warning('Course.get_semester_name() was invoked with non unknown semester.')
            return "nieznany semestr"
        else:
            return self.semester.get_name()

    def get_points(self, student=None):
        '''
            returns points for course, and optionally for certain student
        '''
        pts = None
        if student:
            try:
                pts = PointsOfCourses.objects.filter(course=self, program=student.program_id)
            except PointsOfCourses.DoesNotExist:
                pts = None
        if not pts:
            try:
                pts = PointsOfCourseEntities.objects.filter(entity=self.entity)
            except PointsOfCourseEntities.DoesNotExist:
                pts = None
        if pts:
            return pts[0]
        else:
            return 0


    @staticmethod
    def get_points_for_courses(courses, program):
        '''
            returns points for courses in certain studies program

            format: map with keys = course ids
        '''
        points = {}
        course_points = PointsOfCourses.objects.filter(course__in = courses, \
            program=program).select_related('course')
        courses_without_points = []
        course_entities = []
        for course in courses:
            cpoints = filter(lambda cpoints: cpoints.course == course, course_points)
            if len(cpoints) == 1:
                cpoints = cpoints.pop()
                points[course.pk] = cpoints
            else:
                courses_without_points.append(course)
                course_entities.append(course.entity)
        entity_points = PointsOfCourseEntities.objects.filter( \
            entity__in = course_entities).select_related('entity')
        for course in courses_without_points:
            epoints = filter(lambda cpoints: cpoints.entity == course.entity, \
                entity_points)
            if len(epoints) == 1:
                epoints = epoints.pop()
                points[course.pk] = epoints
        return points

    def serialize_for_ajax(self, student = None, is_recording_open = None):
        from django.core.urlresolvers import reverse
        
        data = {
            'id': self.pk,
            'name': self.name,
            'short_name': self.entity.get_short_name(),
            'type': self.type_id and self.type_id or 1,
            'url': reverse('course-page', args=[self.slug]),
            'is_recording_open': is_recording_open is not None and is_recording_open or (False if (student is None) else \
                self.is_recording_open_for_student(student))
        }

        return data


    class Meta:
        verbose_name = 'przedmiot'
        verbose_name_plural = 'przedmioty'
        app_label = 'courses'
        unique_together = (('name', 'semester'),)
        ordering = ['name']
    
    def __unicode__(self):
        return '%s (%s)' % (self.name, self.get_semester_name())

def recache(sender, **kwargs):
    mcache.clear()
    
signals.post_save.connect(recache)        
signals.post_delete.connect(recache)	
