# -*- coding: utf-8 -*-

from datetime import timedelta, datetime, date
from django.core.exceptions import ObjectDoesNotExist

from django.db import models
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.db.models import signals
from django.core.cache import cache as mcache

from apps.enrollment.courses.models.points import PointsOfCourses, PointsOfCourseEntities
from apps.offer.proposal.exceptions import NotOwnerException
import settings
from student_options import StudentOptions

import logging
logger = logging.getLogger()

class NoRemoved(models.Manager):
    """ Manager for course objects with visible semester """
    def get_query_set(self):
        """ Returns all courses which have marked semester as visible """
        return super(NoRemoved, self).get_query_set().filter(deleted=False, owner__isnull=False)

class CourseEntity(models.Model):

    statuses = ((0, u'Wersja robocza'),(1, u'W ofercie'),(2, u'Poddana pod głosowanie'),)
    semesters = (('u', 'nieoznaczony'), ('z', 'zimowy'), ('l', 'letni'))
    ectslist = [(x, str(x)) for x in range(1, 15) ]

    hours = [(15, '15'), (30, '30'), (45, '45'), (60, '60')]

    """entity of particular course title"""
    name         = models.CharField(max_length=100,
                              verbose_name='nazwa')
    shortName    = models.CharField(max_length=30,
                              verbose_name='skrócona nazwa',
                              null=True, blank=True,
                              help_text=u'Opcjonalna skrócona nazwa, używana na np. planie. Przykłady: JFiZO, AiSD')
    status   = models.IntegerField(choices=statuses, default=1, help_text=u'Wersja robocza widoczna jest jedynie dla jej autora')

    semester = models.CharField(max_length=1, choices=semesters, default='u', verbose_name='semestr')

    type         = models.ForeignKey('Type',
                              verbose_name='rodzaj',
                              null=True)
    description  = models.TextField(verbose_name='opis',
                              null=True, blank=True,
                              default='')

    requirements = models.ManyToManyField("self",
                                verbose_name='wymagane przedmioty',
                                symmetrical=False,
                                blank=True, null=True)
    english      = models.BooleanField(default=False,
                                verbose_name='przedmiot prowadzony w j.angielskim')
    exam         = models.BooleanField(verbose_name='egzamin',
                                default=True)

    web_page     = models.URLField(verbose_name='strona www', null=True, blank=True)
    ects         = models.IntegerField(choices=ectslist, null=True, blank=True)
    lectures = models.IntegerField(choices=hours, null=True, blank=True)
    exercises  = models.IntegerField(choices=hours, null=True, blank=True)
    laboratories  = models.IntegerField(choices=hours, null=True, blank=True)
    repetitions = models.IntegerField(choices=hours, null=True, blank=True)

    deleted = models.BooleanField(verbose_name='ukryty', default=False)
    owner   = models.ForeignKey('users.Employee', verbose_name='prowadzący', blank=True, null=True)
    slug    = models.SlugField(max_length=255, unique=True, verbose_name='odnośnik', null=True)

    created = models.DateTimeField(verbose_name='Utworzono', auto_now_add=True)
    edited  = models.DateTimeField(verbose_name='Ostatnia zmiana', auto_now=True)


    in_prefs = models.BooleanField(verbose_name='w preferencjach', default=True)

    have_review_lecture = models.NullBooleanField(verbose_name=u'Posiada repetytorium', null=True, blank=True)
    have_lecture = models.NullBooleanField(verbose_name=u'Posiada wykład', null=True, blank=True)
    have_tutorial = models.NullBooleanField(verbose_name=u'Posiada ćwiczenia', null=True, blank=True)
    have_lab = models.NullBooleanField(verbose_name=u'Posiada wykład', null=True, blank=True)
    have_tutorial_lab = models.NullBooleanField(verbose_name=u'Posiada ćwiczenio-pracownię', null=True, blank=True)
    have_seminar = models.NullBooleanField(verbose_name=u'Posiada seminarium', null=True, blank=True)
    have_project = models.NullBooleanField(verbose_name=u'Posiada projekt', null=True, blank=True)

    usos_kod = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name=u'Kod przedmiotu w usos', help_text='UWAGA! Nie edytuj tego pola sam!')

    objects   = models.Manager()
    noremoved = NoRemoved()

    class Meta:
        verbose_name = 'Podstawa przedmiotu'
        verbose_name_plural = 'Podstawy przedmiotów'
        app_label = 'courses'
        ordering = ['name']
        
    def __unicode__(self):
        return '%s' % (self.name, )


    def test_have(self, name):
        if self.__getattribute__(name):
            return  self.__getattribute__(name)

        return self.type.__getattribute__(name)

    def test_have_review_lecture(self):
        return self.test_have('have_review_lecture')

    def test_have_lecture(self):
        return self.test_have('have_lecture')

    def test_have_tutorial(self):
        return self.test_have('have_tutorial')

    def test_have_lab(self):
        return self.test_have('have_lab')

    def test_have_tutorial_lab(self):
        return self.test_have('have_tutorial_lab')

    def test_have_seminar(self):
        return self.test_have('have_seminar')

    def test_have_project(self):
        return self.test_have('have_project')


    def get_short_name(self):
        if self.shortName is None:
            return self.name
        else:
            return self.shortName

    def save(self, *args, **kwargs):
        super(CourseEntity, self).save(*args, **kwargs)

        if not self.slug:
            self.slug = slugify('%d_%s' % (self.pk, self.name,))

        super(CourseEntity, self).save(*args, **kwargs)

    def is_summer(self):
        return self.semester == 'l'

    def is_winter(self):
        return self.semester == 'z'

    def get_all_voters(self, year=None):
        from apps.offer.vote.models.single_vote import SingleVote
        from apps.offer.vote.models.system_state import SystemState

        if not year:
            year = date.today().year
        current_state = SystemState.get_state(year)

        votes = SingleVote.objects.filter(value__gte=1, state=current_state, entity=self).select_related('student', 'student__user').order_by('student__matricula')

        return [vote.student for vote in votes]

    @staticmethod
    def get_vote():
        return CourseEntity.noremoved.filter(status=2)

    @staticmethod
    def get_voters():
        from apps.offer.vote.models.single_vote import SingleVote
        from apps.offer.vote.models.system_state import SystemState

        year = date.today().year
        current_state = SystemState.get_state(year)

        return SingleVote.objects.distinct('student').filter(state=current_state)

    @staticmethod
    def get_proposals():
        return CourseEntity.noremoved.filter(status__gte=1)\
                .select_related('type', 'owner', 'owner__user')

    @staticmethod
    def get_proposal(slug):
        return CourseEntity.noremoved.prefetch_related('requirements').get(slug=slug)

    @staticmethod
    def get_employee_proposals(user):
        return CourseEntity.noremoved.filter(owner=user.employee)

    @staticmethod
    def get_employee_proposal(user, slug):
        proposal = CourseEntity.noremoved.get(slug=slug)

        if user.is_staff or proposal.owner == user.employee:
            return proposal
        else:
            raise NotOwnerException

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
    entity  = models.ForeignKey(CourseEntity, verbose_name='podstawa przedmiotu')
    name = models.CharField(max_length=255, verbose_name='nazwa przedmiotu')
    semester = models.ForeignKey('Semester', null=True, verbose_name='semestr')
    slug = models.SlugField(max_length=255, unique=True, verbose_name='odnośnik', null=True)
    type = models.ForeignKey('Type', verbose_name='rodzaj')
    teachers = models.ManyToManyField('users.Employee', verbose_name='prowadzący', blank=True)
    description = models.TextField(verbose_name='opis', blank=True, default='') 
    lectures = models.IntegerField(verbose_name='wykład', null=True, default=0)
    repetitions = models.IntegerField(verbose_name='Repetytorium', null=True, default=0)
    exercises = models.IntegerField(verbose_name='ćwiczenia', null=True, default=0)
    laboratories = models.IntegerField(verbose_name='pracownia', null=True, default=0)
    exercises_laboratories = models.IntegerField(verbose_name='ćw+prac', null=True, default=0)
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

    dyskretna_l  = models.BooleanField(default=False)
    numeryczna_l = models.BooleanField(default=False)

    objects = models.Manager()
    visible = VisibleManager()

    def save(self, *args, **kwargs):
        super(Course, self).save(*args, **kwargs)
        if not self.pk:
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

        if not self.slug:
            self.slug = slugify('%d %s %s' % (self.pk, self.name))

        super(Course, self).save(*args, **kwargs)

    def student_is_in_ects_limit(self, student):
        #TODO: test me!
        from apps.enrollment.courses.models import Semester
        semester = Semester.get_current_semester()

        return semester.get_current_limit() < student.get_ects_with_course(semester, self)



    def votes_count(self, semester=None):
        from apps.offer.vote.models import SingleVote
        return SingleVote.objects\
                 .filter(Q(course=self), Q(state__semester_summer=self.semester) | Q(state__semester_winter=self.semester))\
                 .count()


    def is_recording_open_for_student(self, student=None):
        """ gives the answer to question: is course opened for apps.enrollment for student at the very moment? """

        if not student:
            return False

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
        from apps.offer.vote.models.single_vote import SingleVote

        try:
            vote = SingleVote.objects.get(Q(course=self), Q(student=student), Q(state__semester_winter=self.semester) | Q(state__semester_summer=self.semester) )
            interval = timedelta(minutes=(-1440)*vote.correction+4320)
        except ObjectDoesNotExist:
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
        from apps.users.models import Program
        '''
            returns points for course, and optionally for certain student
        '''
        pts = None
        if student:
            if ( student.numeryczna_l and self.numeryczna_l) or (student.dyskretna_l and self.dyskretna_l):
                import settings
                program = Program.objects.get(id=settings.M_PROGRAM)
            else:
                program = student.program_id
            try:
                pts = PointsOfCourses.objects.filter(course=self, program=program)
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
    def get_points_for_courses(courses, program, student=None):
        '''
            returns points for courses in certain studies program

            format: map with keys = course ids
        '''
        points = {}
        course_points = PointsOfCourses.objects.filter(course__in = courses,
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
#
#signals.post_save.connect(recache)
#signals.post_delete.connect(recache)
