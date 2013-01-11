# -*- coding: utf-8 -*-

from datetime import date
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

from django.db import models
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.db.models import signals
from django.core.cache import cache as mcache

from apps.enrollment.courses.models.points import PointsOfCourseEntities
from apps.offer.proposal.exceptions import NotOwnerException
import settings
from student_options import StudentOptions

import logging
from timedelta.fields import TimedeltaField
logger = logging.getLogger()

class NoRemoved(models.Manager):
    """ Manager for course objects with visible semester """
    def get_query_set(self):
        """ Returns all courses which have marked semester as visible """
        return super(NoRemoved, self).get_query_set().filter(deleted=False, owner__isnull=False)


class DefaultCourseManager(models.Manager):
    def get_query_set(self):
        """ Returns all courses which have marked semester as visible """
        return super(DefaultCourseManager, self).get_query_set().select_related('entity', 'information')

statuses = ((0, u'Wersja robocza'),(1, u'W ofercie'),(2, u'Poddana pod głosowanie'),)
semesters = (('u', 'nieoznaczony'), ('z', 'zimowy'), ('l', 'letni'))
ectslist = [(x, str(x)) for x in range(1, 16) ]

class CourseEntity(models.Model):
    """entity of particular course title"""

    information = models.ForeignKey('CourseDescription', null=True, blank=True)

    #Test name
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
    english      = models.BooleanField(default=False,
                                verbose_name='przedmiot prowadzony w j.angielskim')
    exam         = models.BooleanField(verbose_name='egzamin',
                                default=True)

    suggested_for_first_year = models.BooleanField(verbose_name='polecany dla pierwszego roku')


    web_page     = models.URLField(verbose_name='strona www', null=True, blank=True)
    ects         = models.IntegerField(null=True, blank=True)
    lectures = models.IntegerField(null=True, blank=True)
    exercises  = models.IntegerField(null=True, blank=True)
    laboratories  = models.IntegerField(null=True, blank=True)
    repetitions = models.IntegerField(null=True, blank=True)
    seminars = models.IntegerField( null=True, blank=True, verbose_name='seminaria')
    exercises_laboratiories = models.IntegerField(null=True, blank=True, verbose_name='ćwiczenio-pracownie')

    deleted = models.BooleanField(verbose_name='ukryty', default=False)
    owner   = models.ForeignKey('users.Employee', verbose_name='opiekun', blank=True, null=True)
    slug    = models.SlugField(max_length=255, unique=True, verbose_name='odnośnik (nazwa pojawiająca się w urlach)', null=True)

    created = models.DateTimeField(verbose_name='Utworzono', auto_now_add=True)
    edited  = models.DateTimeField(verbose_name='Ostatnia zmiana', auto_now=True)

    in_prefs = models.BooleanField(verbose_name='w preferencjach', default=True)


    dyskretna_l     = models.BooleanField(default=False)
    numeryczna_l    = models.BooleanField(default=False)
    algorytmy_l     = models.BooleanField(default=False)
    programowanie_l = models.BooleanField(default=False)

    usos_kod = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name=u'Kod przedmiotu w usos', help_text='UWAGA! Nie edytuj tego pola sam!')

    objects   = models.Manager()
    noremoved = NoRemoved()


    def save(self, *args, **kwargs):
        """
        Overloaded save method - during save autocreate slug field

        @param args: like model save args
        @param kwargs: like model save kwargs
        @return: nothing
        """
        super(CourseEntity, self).save(*args, **kwargs)

        if not self.slug:
            self.slug = slugify('%d_%s' % (self.pk, self.name,))

        super(CourseEntity, self).save(*args, **kwargs)

    def __unicode__(self):
        return '%s' % (self.name, )

    class Meta:
        verbose_name = 'Podstawa przedmiotu'
        verbose_name_plural = 'Podstawy przedmiotów'
        app_label = 'courses'
        ordering = ['name']



    def get_short_name(self):
        """
        If entity have shortName (e.g. JFiZO for Języki Formalne i Złożoność Obliczeniowa) return it.
        Otherwise return full name

        @return: String
        """
        if self.shortName is None:
            return self.name
        else:
            return self.shortName



    @property
    def have_review_lecture(self):
        """
        Return True if entity have more than 0 hours of repetitions

        @return: Boolean
        """
        return self.repetitions and self.repetitions > 0

    @property
    def have_lecture(self):
        """
        Return True if entity have more than 0 hours of lecture

        @return: Boolean
        """
        return self.lectures and self.lectures > 0

    @property
    def have_tutorial(self):
        """
        Return True if entity have more than 0 hours of tutorial

        @return: Boolean
        """
        return self.exercises and self.exercises > 0

    @property
    def have_lab(self):

        """
        Return True if entity have more than 0 hours of laboratiories

        @return: Boolean
        """
        return self.laboratories and self.laboratories > 0

    @property
    def have_tutorial_lab(self):

        """
        Return True if entity have more than 0 hours of mixed tutorial and labs

        @return: Boolean
        """
        return self.exercises_laboratiories and self.exercises_laboratiories > 0

    @property
    def have_seminar(self):

        """
        Return True if entity have more than 0 hours of seminars

        @return: Boolean
        """
        return self.seminars and self.seminars > 0


    def is_summer(self):
        """
        Return True if entity is in summer semester

        @return Boolean
        """
        return self.semester == 'l'

    def is_winter(self):
        """
        Return True if entity is in winter semester

        @return Boolean
        """
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
        return CourseEntity.noremoved.get(slug=slug)

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
    """
    Instacja Przedmiotu w danym przedmiocie
    """
    entity      = models.ForeignKey(CourseEntity, verbose_name='podstawa przedmiotu')
    information = models.ForeignKey('CourseDescription', verbose_name='opis', null=True, blank=True)

    slug = models.SlugField(max_length=255, unique=True, verbose_name='odnośnik', null=True)
    semester = models.ForeignKey('Semester', null=True, verbose_name='semestr')
    teachers = models.ManyToManyField('users.Employee', verbose_name='prowadzący', blank=True)

    notes    = models.TextField(null=True, blank=True, verbose_name='uwagi do tej edyci przedmiotu')
    web_page = models.URLField( verbose_name = 'Strona WWW przedmiotu',
                                verify_exists= True,
								blank        = True,
                                null         = True )

    english = models.BooleanField(default=False, verbose_name='przedmiot prowadzony w j.angielskim')
    #chceck this!
    students_options = models.ManyToManyField('users.Student',
                                              verbose_name='opcje studentów',
                                              through='StudentOptions')

    records_start = models.DateTimeField(verbose_name=u'Początek zapisów', null=True, blank=True)
    records_end = models.DateTimeField(verbose_name=u'Koniec zapisów', null=True, blank=True)

    objects = DefaultCourseManager()
    visible = VisibleManager()

    """
    getters
    """

    @property
    def exam(self):
        return self.entity.exam

    @property
    def suggested_for_first_year(self):
        return self.entity.suggested_for_first_year

    @property
    def name(self):
        return self.entity.name

    @property
    def description(self):
        return self.information.description

    @property
    def type(self):
        return self.entity.type

    @property
    def lectures(self):
        return self.entity.lectures + self.information.lectures

    @property
    def repetitions(self):
        return self.entity.repetitions + self.information.repetitions

    @property
    def exercises(self):
        return self.entity.exercises + self.information.exercises

    @property
    def exercises_laboratories(self):
        return self.entity.exercises_laboratiories + self.information.exercises_laboratories

    @property
    def laboratories(self):
        return self.entity.laboratories + self.information.laboratories

    @property
    def seminars(self):
        return self.entity.seminars + self.information.seminars

    @property
    def requirements(self):
        return self.information.requirements

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify('%d %s %s' % (self.pk, self.name))

        super(Course, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('course-page', args=[str(self.slug)])

    def student_is_in_ects_limit(self, student):
        #TODO: test me!
        from apps.enrollment.courses.models import Semester
        semester = Semester.get_current_semester()

        return semester.get_current_limit() < student.get_ects_with_course(semester, self)


    def get_all_enrolled_emails(self):
        from apps.enrollment.records.models import Record
        return Record.objects.filter(group__course=self, status='1').values_list('student__user__email', flat=True).distinct()


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
            interval = datetime.timedelta(minutes=4320) #TODO: 3 dni -> to powinno chyba wylądować w konfigu

        if self.records_start and self.records_end and self.records_start <= datetime.datetime.now() <= self.records_end:
            return True

        if records_opening == None:
            return False
        else:
            student_opening = records_opening - student.get_t0_interval()
            if student_opening + interval < datetime.datetime.now():
                if records_closing == None:
                    return True
                else:
                    return datetime.datetime.now() < records_closing
            else:
                return False

    def get_enrollment_opening_time(self, student):
        """ returns course opening time as datetime object or None if course is opened / was opened """
        records_opening = self.semester.records_opening
        from apps.offer.vote.models.single_vote import SingleVote

        try:
            vote = SingleVote.objects.get(Q(course=self), Q(student=student), Q(state__semester_winter=self.semester) | Q(state__semester_summer=self.semester) )
            interval = datetime.timedelta(minutes=(-1440)*vote.correction+4320)
        except ObjectDoesNotExist:
            interval = datetime.timedelta(minutes=4320)

        if records_opening == None:
            return False
        else:
            student_opening = records_opening - student.get_t0_interval()
            if student_opening + interval < datetime.datetime.now():
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
        """
            @param student: (optional) :model:'users.Student'

            @return :model:'courses.Points' or :model:'courses.PointsOfCourseEntities' both have the same interface
        """

        from apps.enrollment.courses.models.points import Points
        if student:
            try:
                return Points.get_for_student(student=student,course=self)
            except ObjectDoesNotExist:
                return None

        return PointsOfCourseEntities.get_course_points(self)



    def serialize_for_ajax(self, student = None, is_recording_open = None):
        from django.core.urlresolvers import reverse
        
        data = {
            'id': self.pk,
            'name': self.name,
            'short_name': self.entity.get_short_name(),
            'type': self.type.id and self.type.id or 1,
            'url': reverse('course-page', args=[self.slug]),
            'is_recording_open': is_recording_open is not None and is_recording_open or (False if (student is None) else \
                self.is_recording_open_for_student(student))
        }

        return data


    def has_exam_reservation(self):
        """
            Return True if  Course have reservation for exam
        """

        from apps.schedule.models import Event

        if not self.exam:
            return False

        if Event.objects.filter(course=self, type='0').exists():
            return True

        return False

    @staticmethod
    def get_courses_with_exam(semester):
        return Course.objects.filter(semester=semester, entity__exam=True)


    class Meta:
        verbose_name = 'przedmiot'
        verbose_name_plural = 'przedmioty'
        app_label = 'courses'
        ordering = ['entity__name']
        permissions = (
                    ("view_stats", u"Może widzieć statystyki"),
                )
    
    def __unicode__(self):
        return '%s (%s)' % (self.name, self.get_semester_name())

def recache(sender, **kwargs):
    mcache.clear()
#
#signals.post_save.connect(recache)
#signals.post_delete.connect(recache)


class CourseDescription(models.Model):

    """
    Przechowuje rewizję informacji o przedmiocie.
    Powiązania: :model:'course.CourseEntity'
    """

    entity = models.ForeignKey(CourseEntity) #Podstawa do ktorej jestesmy przypisani
    author = models.ForeignKey('users.Employee')

    is_ready = models.BooleanField()

    description = models.TextField(verbose_name='opis', blank=True, default='')

    lectures     = TimedeltaField(verbose_name='wykład', blank=True, null=True, default=datetime.timedelta(hours=0))
    repetitions  = TimedeltaField(verbose_name='Repetytorium', blank=True,null=True, default=datetime.timedelta(hours=0))
    exercises    = TimedeltaField(verbose_name='ćwiczenia', blank=True, null=True, default=datetime.timedelta(hours=0))
    laboratories = TimedeltaField(verbose_name='pracownia', blank=True, null=True, default=datetime.timedelta(hours=0))
    seminars     = TimedeltaField(default=datetime.timedelta(hours=0), null=True, blank=True, verbose_name='seminaria')
    exercises_laboratories = TimedeltaField(verbose_name='ćw+prac', blank=True, null=True, default=datetime.timedelta(hours=0))

    requirements = models.ManyToManyField(CourseEntity, verbose_name='wymagania', related_name='+', blank=True)
    exam = models.BooleanField(verbose_name='egzamin')


    class Meta:
        verbose_name = 'opis przedmiotu'
        verbose_name_plural = 'opisy przedmiotu'
        app_label = 'courses'



"""
CREATE OR REPLACE VIEW courses_points AS
 SELECT cc.semester_id, au.id AS student_id, cc.id AS course_id, COALESCE(
        CASE
            WHEN au.numeryczna_l AND cc.numeryczna_l OR au.dyskretna_l AND cc.dyskretna_l THEN ( SELECT cp.value
               FROM courses_pointsofcourses cp
              WHERE cp.course_id = cc.id AND cp.program_id = 1)
            ELSE ( SELECT cp.value
               FROM courses_pointsofcourses cp
              WHERE cp.course_id = cc.id AND cp.program_id = au.program_id)
        END::integer, (( SELECT cpe.value
           FROM courses_pointsofcourseentities cpe
          WHERE cpe.entity_id = cc.entity_id))::integer, 0) AS value, ( SELECT count(*) AS count
           FROM records_record rr
      LEFT JOIN courses_group cg ON rr.group_id = cg.id
     WHERE cg.course_id = cc.id AND rr.status::integer = 1 AND rr.student_id = au.id) AS groups
   FROM users_student au, courses_course cc;
"""