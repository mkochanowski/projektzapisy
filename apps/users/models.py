# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

from apps.users.exceptions import NonEmployeeException, NonStudentException
from apps.enrollment.courses.models.points import PointTypes

import datetime

from fereol import settings

import logging
logger = logging.getLogger()

class BaseUser(models.Model):
    '''
    User abstract class. For every app user there is entry in django.auth.
    We do not inherit after User directly, because of problems with logging beckend etc.
    '''
    user = models.OneToOneField(User, verbose_name="Użytkownik")
    receive_mass_mail_enrollment = models.BooleanField(
        default = True, 
        verbose_name="otrzymuje mailem ogłoszenia Zapisów")
    receive_mass_mail_offer = models.BooleanField(
        default = True, 
        verbose_name="otrzymuje mailem ogłoszenia OD")
    receive_mass_mail_grade = models.BooleanField(
        default = True, 
        verbose_name="otrzymuje mailem ogłoszenia Oceny Zajęć")
        
    def get_full_name(self):
        return self.user.get_full_name()
    get_full_name.short_description = 'Użytkownik'
    
    @staticmethod
    def get(user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.error('Getter(user_id = %d) in BaseUser throws User.DoesNotExist exception.' % user_id )
            raise NonUserException
        return user

    @staticmethod
    def is_student(user):
        try:
            student = user.student
            return True
        except:
            return False

    @staticmethod
    def is_employee(user):
        try:
            employee = request.user.employee
            return True
        except:
            return False

    def __unicode__(self):
        return self.get_full_name
    
    class Meta:
        abstract = True



class Employee(BaseUser):
    '''
    Employee.
    '''
    consultations = models.TextField(verbose_name="konsultacje")
    homepage = models.URLField(verify_exists=True, verbose_name='strona domowa', default="")
    room = models.PositiveIntegerField(verbose_name="pokój", null=True)
        
    def has_privileges_for_group(self, group_id):
        """
        Method used to verify whether user is allowed to create a poll for certain group 
        (== he is an admin, a teacher for this course or a teacher for this group)
        """
        from apps.enrollment.courses.models import Group

        try:
            group = Group.objects.get(pk=group_id)
            return ( group.teacher == self or self in group.course.teachers.all() or self.user.is_staff )
        except:
            logger.error('Function Employee.has_privileges_for_group(group_id = %d) throws Group.DoesNotExist exception.' % group_id)
        return False

    @staticmethod
    def get_list(begin):
        def next_char(begin):
            return chr(ord(begin) + 1)
        if begin == 'Z':
            return Employee.objects.filter(user__last_name__gte=begin).\
                    select_related().order_by('user__last_name', 'user__first_name')
        elif begin == 'All':
            return Employee.objects.all().\
                    select_related().order_by('user__last_name', 'user__first_name')
        else:
            end = next_char(begin)
            return Employee.objects.filter(user__last_name__range=(begin, end)).\
                    select_related().order_by('user__last_name', 'user__first_name')




    @staticmethod
    def get_all_groups_in_semester(user_id):
        from apps.enrollment.courses.models import Group, Semester

        user = User.objects.get(id=user_id)
        semester = Semester.get_current_semester()
        try:
            employee = user.employee
            groups = Group.objects.filter(teacher=employee, course__semester=semester)
        except Employee.DoesNotExist:
             logger.error('Function Employee.get_all_groups(user_id = %d) throws Employee.DoesNotExist exception.' % user_id )
             raise NonEmployeeException()
        return groups

    @staticmethod
    def get_all_groups(user_id):
        from apps.enrollment.courses.models import Group

        user = User.objects.get(id=user_id)
        try:
            employee = user.employee
            groups = Group.objects.filter(teacher=employee)
        except Employee.DoesNotExist:
             logger.error('Function Employee.get_all_groups(user_id = %d) throws Employee.DoesNotExist exception.' % user_id )
             raise NonEmployeeException()
        return groups
    
    @staticmethod
    def get_schedule(user_id):
        user = User.objects.get(id=user_id)
        try:
            employee = user.employee
            groups = [g for g in Employee.get_all_groups_in_semester(user_id) ]
            courses = set([group.course for group in groups])
            for group in groups:
                group.terms_ = group.get_all_terms()
                group.course_ = group.course
            return groups
        except Employee.DoesNotExist:
             logger.error('Function Employee.get_schedule(user_id = %d) throws Employee.DoesNotExist exception.' % user_id )
             raise NonEmployeeException()
         
    class Meta:
        verbose_name = 'pracownik'
        verbose_name_plural = 'Pracownicy'
        app_label = 'users'
      
    def __unicode__(self):
        return unicode(self.user.get_full_name())

class Student(BaseUser):
    ''' 
    Student.
    '''
    matricula = models.CharField(max_length=20, default="", unique=True, verbose_name="Numer indeksu")
    ects = models.PositiveIntegerField(verbose_name="punkty ECTS", default=0)
    records_opening_bonus_minutes = models.PositiveIntegerField(default=0, verbose_name="Przyspieszenie otwarcia zapisów (minuty)")
    program = models.ForeignKey('Program', verbose_name='Program Studiów', null=True, default=None)
    block = models.BooleanField(verbose_name="blokada planu", default = False)
    semestr = models.PositiveIntegerField(default=0, verbose_name="Semestr")
    status = models.PositiveIntegerField(default=0, verbose_name="Status")
    status.help_text = "0 - aktywny student, 1 - skreślony student"


    def get_type_of_studies(self):
        """ returns type of studies """
        semestr = {1:'pierwszy',2:'drugi',3:'trzeci',4:'czwarty',5:'piąty',6:'szósty',7:'siódmy',8:'ósmy',9:'dziewiąty',10:'dziesiąty',0:'niezdefiniowany'}[self.semestr]
        return '%s, semestr %s' % (self.program , semestr)
    get_type_of_studies.short_description = 'Studia'

    def get_t0_interval(self):
        return datetime.timedelta(minutes=(self.records_opening_bonus_minutes + self.ects * settings.ECTS_BONUS)) #TODO: Sprawdzić, czy student brał udział w ocenie zajęć, jezeli tak - dodać datetime.timedelta(days=1) -- poprawić przy merge'owaniu z oceną...

    def get_records_history(self):
        '''
        Returns list of ids of course s that student was enrolled for.
        '''
        from apps.enrollment.courses.models import Semester

        default_semester = Semester.get_default_semester()
        records = self.records.exclude(group__course__semester = default_semester)
        records_list = map(lambda x: x.group.course.entity.id, records)
        return list(frozenset(records_list))


    @staticmethod
    def get_list(begin = 'A'):
        def next_char(begin):
            return chr(ord(begin) + 1)
        if begin == 'Z':
            return Student.objects.filter(user__last_name__gte=begin).\
                    select_related().order_by('user__last_name', 'user__first_name')
        elif begin == 'All':
            return Student.objects.all().\
                    select_related().order_by('user__last_name', 'user__first_name')
        else:
            end = next_char(begin)
            return Student.objects.filter(user__last_name__range=(begin, end)).\
                    select_related().order_by('user__last_name', 'user__first_name')

    @staticmethod
    def get_all_groups(student):
        try:
            groups = map(lambda x: x.group, student.records.filter(status="1").\
                        select_related('group', 'group__teacher',
                                      'group__course__semester',
                                      'group__course__term'))
        except Student.DoesNotExist:
             logger.error('Function Student.get_all_groups(student = %d)' + \
             'throws Student.DoesNotExist exception.' % student.pk )
             raise NonStudentException()
        return groups
    
    @staticmethod
    def get_schedule(student):
        try:
            groups = [g for g in Student.get_all_groups(student) if g.course.semester.is_current_semester()]
            courses = set([group.course for group in groups])
            for group in groups:
                group.terms_ = group.get_all_terms()
                group.course_ = group.course
            return groups
        except Student.DoesNotExist:
             logger.error('Function Student.get_schedule(user_id = %d) throws Student.DoesNotExist exception.' % user.id )
             raise NonStudentException()
    
    def records_set_locked(self, locked):
        self.block = locked
        self.save()

    @staticmethod
    def get_zamawiany(user_id):
        try:
            user = User.objects.get(id=user_id)
            student = Student.objects.get(user=user)
            zamawiany = StudiaZamawiane.objects.get(student=student)
            return zamawiany
        except (User.DoesNotExist, Student.DoesNotExist, StudiaZamawiane.DoesNotExist):
             return None

    def zamawiany(self):
        return StudiaZamawiane.objects.get(student=self);

    def is_zamawiany(self):
        try:
            self.zamawiany()
            return True
        except StudiaZamawiane.DoesNotExist:
            return False
        
    class Meta:
        verbose_name = 'student'
        verbose_name_plural = 'studenci'
        app_label = 'users'
    
    def __unicode__(self):
        return unicode(self.user.get_full_name())


class Program( models.Model ):
    """
        Program of student studies
    """
    name = models.CharField(max_length=50, unique=True, verbose_name="Program")
    type_of_points = models.ForeignKey(PointTypes, verbose_name='rodzaj punktów')

    class Meta:
        verbose_name = 'Program studiów'
        verbose_name_plural = 'Programy studiów'

    def __unicode__(self):
        return self.name

class StudiaZamawiane(models.Model):
    """
        Model przechowuje dodatkowe informacje o studentach zamawianych
    """
    student = models.OneToOneField(Student, verbose_name='Student')
    points =  models.FloatField(verbose_name='Punkty')
    comments = models.TextField(verbose_name='Uwagi', blank=True)
    bank_account = models.CharField(max_length=40, blank=True, verbose_name="Numer konta bankowego")

    class Meta:
        verbose_name = 'Studia zamawiane'
        verbose_name_plural = 'Studia zamawiane'

    def __unicode__(self):
        return 'Student zamawiany: '+str(self.student)
