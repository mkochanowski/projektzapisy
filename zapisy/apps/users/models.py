# -*- coding: utf-8 -*-
import datetime
import logging

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from apps.users.exceptions import NonUserException
from apps.users.managers import GettersManager, T0Manager

logger = logging.getLogger()

EMPLOYEE_STATUS_CHOICES = [(0, 'aktywny'), (1, 'nieaktywny')]


class Related(models.Manager):
    def get_queryset(self):
        return super(Related, self).get_queryset().select_related('user')

class BaseUser(models.Model):
    '''
    User abstract class. For every app user there is entry in django.auth.
    We do not inherit after User directly, because of problems with logging beckend etc.
    '''
    receive_mass_mail_enrollment = models.BooleanField(
        default=True,
        verbose_name="otrzymuje mailem ogłoszenia Zapisów")
    receive_mass_mail_offer = models.BooleanField(
        default=True,
        verbose_name="otrzymuje mailem ogłoszenia OD")
    receive_mass_mail_grade = models.BooleanField(
        default=True,
        verbose_name="otrzymuje mailem ogłoszenia Oceny Zajęć")
    last_news_view = models.DateTimeField(default=datetime.datetime.now)

    objects = Related()

    def get_full_name(self):
        return self.user.get_full_name()
    get_full_name.short_description = 'Użytkownik'

    def get_number_of_news(self):
        from apps.news.models import News
        if not hasattr(self, '_count_news'):
            self._count_news = News.objects.exclude(category='-').filter(date__gte=self.last_news_view).count()

        return self._count_news

    @staticmethod
    def get(user_id):
        # type: (object) -> object
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.error('Getter(user_id = %d) in BaseUser throws User.DoesNotExist exception.' % user_id )
            raise NonUserException
        return user

    @staticmethod
    def is_student(user):
        if user:
            return user.groups.filter(name='students').exists()
        return False

    @staticmethod
    def is_employee(user):
        if user:
            return user.groups.filter(name='employees').exists()
        return False

    def __unicode__(self):
        return self.get_full_name

    class Meta:
        abstract = True


class Employee(BaseUser):
    '''
    Employee.
    '''

    user = models.OneToOneField(User, verbose_name="Użytkownik", related_name='employee', on_delete=models.CASCADE)
    consultations = models.TextField(verbose_name="konsultacje", null=True, blank=True)
    homepage = models.URLField(verbose_name='strona domowa', default="", null=True, blank=True)
    room = models.CharField(max_length=20, verbose_name="pokój", null=True, blank=True)
    status = models.PositiveIntegerField(default=0, choices=EMPLOYEE_STATUS_CHOICES, verbose_name="Status")
    title = models.CharField(max_length=20, verbose_name="tytuł naukowy", null=True, blank=True)
    
    def make_preferences(self):
        from apps.offer.preferences.models import Preference

        Preference.make_preferences(self)

    def get_preferences(self):
        from apps.offer.preferences.models import Preference
        return Preference.for_employee(self)

    @staticmethod
    def get_actives():
        return Employee.objects.filter(user__is_active=True).order_by('user__last_name', 'user__first_name'). extra(
                        where=["(SELECT COUNT(*) FROM courses_courseentity WHERE courses_courseentity.status > 0 AND NOT courses_courseentity.deleted AND courses_courseentity.owner_id=users_employee.id)>0"]
        )


    @staticmethod
    def get_list(begin='All'):
        def next_char(begin):
            try:
                return chr(ord(begin) + 1)
            except ValueError:
                return chr(90)
        if begin == 'Z':
            employees = Employee.objects.filter(user__last_name__gte=begin, status=0).\
                    select_related().order_by('user__last_name', 'user__first_name')
        elif begin == 'All':
            employees = Employee.objects.filter(status=0).\
                    select_related().order_by('user__last_name', 'user__first_name')
        else:
            end = next_char(begin)
            employees = Employee.objects.filter(user__last_name__range=(begin, end), status=0).\
                    select_related().order_by('user__last_name', 'user__first_name')

        return employees

    class Meta:
        verbose_name = 'pracownik'
        verbose_name_plural = 'Pracownicy'
        app_label = 'users'
        ordering = ['user__last_name', 'user__first_name']
        permissions = (
            ("mailto_all_students", u"Może wysyłać maile do wszystkich studentów"),
        )

    def __unicode__(self):
        return unicode(self.user.get_full_name())

class Student(BaseUser):
    '''
    Student.
    '''

    user = models.OneToOneField(User, verbose_name="Użytkownik", related_name='student', on_delete=models.CASCADE)
    matricula = models.CharField(max_length=20, default="", unique=True, verbose_name="Numer indeksu")
    ects = models.PositiveIntegerField(verbose_name="punkty ECTS", default=0)
    records_opening_bonus_minutes = models.PositiveIntegerField(default=0, verbose_name="Przyspieszenie otwarcia zapisów (minuty)")
    program = models.ForeignKey('Program', verbose_name='Program Studiów', null=True, default=None, on_delete=models.CASCADE)
    block = models.BooleanField(verbose_name="blokada planu", default = False)
    semestr = models.PositiveIntegerField(default=0, verbose_name="Semestr")
    status = models.PositiveIntegerField(default=0, verbose_name="Status")
    status.help_text = "0 - aktywny student, 1 - skreślony student"

    t0 = models.DateTimeField(null=True, blank=True)

    ects_in_semester = models.SmallIntegerField(default=0)

    dyskretna_l  = models.BooleanField(default=False)
    numeryczna_l = models.BooleanField(default=False)
    algorytmy_l = models.BooleanField(default=False)
    programowanie_l = models.BooleanField(default=False)

    objects = GettersManager()

    def is_active(self):
        return self.status == 0

    def is_isim(self):
        """"Returns True if student's program is "ISIM, dzienne I stopnia", False otherwise."""
        try:
            return self.program == Program.objects.get(name='ISIM, dzienne I stopnia')
        except Program.DoesNotExist:
            return False

    def get_type_of_studies(self):
        """ returns type of studies """
        semestr = {1:'pierwszy',2:'drugi',3:'trzeci',4:'czwarty',5:'piąty',6:'szósty',7:'siódmy',8:'ósmy',9:'dziewiąty',10:'dziesiąty',0:'niezdefiniowany'}[self.semestr]
        return '%s, semestr %s' % (self.program , semestr)
    get_type_of_studies.short_description = 'Studia'

    def participated_in_last_grades(self):
        from apps.grade.ticket_create.models.student_graded import StudentGraded
        return StudentGraded.objects.filter(student=self, semester__in=[45, 239]).count()

    def get_t0_interval(self):
        """ returns t0 for student->start of records between 10:00 and 22:00; !record_opening hour should be 00:00:00! """
        if hasattr(self, '_counted_t0'):
            return self._counted_t0

        base =  self.ects * settings.ECTS_BONUS
        points_for_one_day = 720 # =12h*60m
        points_for_one_night = 720
        number_of_nights_to_add = base / points_for_one_day
        minutes = base + number_of_nights_to_add * points_for_one_night
        minutes += self.records_opening_bonus_minutes
        grade = self.participated_in_last_grades() * 1440
        self._counted_t0 =  datetime.timedelta(minutes=minutes+grade+120)+datetime.timedelta(days=3)
        return self._counted_t0

    def get_points(self, semester=None):
        from apps.enrollment.courses.models import Semester, StudentPointsView
        from apps.enrollment.records.models import Record
        if not semester:
            semester = Semester.objects.get_next()

        records = Record.objects.filter(student=self, group__course__semester=semester, status=1).values_list('group__course__entity_id', flat=True).distinct()

        return StudentPointsView.get_points_for_entities(self, records)

    def get_points_with_course(self, course, semester=None):
        from apps.enrollment.courses.models import Semester, StudentPointsView
        from apps.enrollment.records.models import Record
        if not semester:
            semester = Semester.objects.get_next()

        records = Record.objects.filter(student=self, group__course__semester=semester, status=1).values_list('group__course__entity_id', flat=True).distinct()
        if course.entity_id not in records:
            records = list(records) + [course.entity_id]

        return StudentPointsView.get_points_for_entities(self, records)

    @classmethod
    def get_active_students(cls):
        return cls.objects.filter(status=0)

    @staticmethod
    def get_list(begin='All'):
        def next_char(begin):
            try:
                return chr(ord(begin) + 1)
            except ValueError:
                return chr(90)
        if begin == 'Z':
            return Student.objects.filter(status=0,user__last_name__gte=begin).\
                    select_related().order_by('user__last_name', 'user__first_name')
        elif begin == 'All':
            return Student.objects.filter(status=0).\
                    select_related().order_by('user__last_name', 'user__first_name')
        else:
            end = next_char(begin)
            return Student.objects.filter(status=0,user__last_name__range=(begin, end)).\
                    select_related().order_by('user__last_name', 'user__first_name')

    def records_set_locked(self, locked):
        self.block = locked
        self.save()

    def is_first_year_student(self):
        return (self.semestr in [1,2]) and (self.program.id in [0,2])

    def is_fresh_student(self):
        return True

    class Meta:
        verbose_name = 'student'
        verbose_name_plural = 'studenci'
        app_label = 'users'
        ordering = ['user__last_name', 'user__first_name']

    def __unicode__(self):
        return unicode(self.user.get_full_name())


class Program( models.Model ):
    """
        Program of student studies
    """
    name = models.CharField(max_length=50, unique=True, verbose_name="Program")
    type_of_points = models.ForeignKey('courses.PointTypes', verbose_name='rodzaj punktów', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Program studiów'
        verbose_name_plural = 'Programy studiów'

    def __unicode__(self):
        return self.name

class OpeningTimesView(models.Model):
    student  = models.OneToOneField(Student, primary_key=True,on_delete=models.CASCADE,
                                    related_name='opening_times')
    course   = models.ForeignKey('courses.Course', on_delete=models.CASCADE)
    semester = models.ForeignKey('courses.Semester', on_delete=models.CASCADE)
    opening_time = models.DateTimeField()

    objects = T0Manager()

    class Meta:
        app_label = 'users'
