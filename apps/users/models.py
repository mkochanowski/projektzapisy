# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

from exceptions import NonEmployeeException, NonStudentException
from apps.users.exceptions import NonEmployeeException, NonStudentException
from apps.enrollment.subjects.models import Group, Semester

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
        (== he is an admin, a teacher for this subject or a teacher for this group)
        """
        try:
            group = Group.objects.get(pk=group_id)
            return ( group.teacher == self or self in group.subject.teachers.all() or self.user.is_staff )
        except:
            logger.error('Function Employee.has_privileges_for_group(group_id = %d) throws Group.DoesNotExist exception.' % group_id)
        return False
            
    @staticmethod
    def get_all_groups(user_id):
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
            groups = [g for g in Employee.get_all_groups(user_id) ]
            subjects = set([group.subject for group in groups])
            for group in groups:
                group.terms_ = group.get_all_terms()
                group.subject_ = group.subject
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
    records_opening_delay_minutes = models.PositiveIntegerField(default=0, verbose_name="Opóźnienie w otwarciu zapisów (minuty)")
    program = models.ForeignKey('Program', verbose_name='Program Studiów', null=True, default=None)
    block = models.BooleanField(verbose_name="blokada planu", default = False)
    semestr = models.PositiveIntegerField(default=0, verbose_name="Semestr")

    def get_type_of_studies(self):
        """ returns type of studies """
        semestr = {1:'pierwszy',2:'drugi',3:'trzeci',4:'czwarty',5:'piąty',6:'szósty',7:'siódmy',8:'ósmy',9:'dziewiąty',10:'dziesiąty',0:'niezdefiniowany'}[self.semestr]
        return '%s, semestr %s' % (self.program , semestr)
    get_type_of_studies.short_description = 'Studia'

    def get_t0_interval(self):
        return datetime.timedelta(minutes=(self.records_opening_delay_minutes + self.ects * settings.ECTS_BONUS)) #TODO: Sprawdzić, czy student brał udział w ocenie zajęć, jezeli tak - dodać datetime.timedelta(days=1) -- poprawić przy merge'owaniu z oceną...

    def get_records_history(self):
        '''
        Returns list of ids of subject s that student was enrolled for.
        '''
        default_semester = Semester.get_default_semester()
        records = self.records.exclude(group__subject__semester = default_semester)
        records_list = map(lambda x: x.group.subject.entity.id, records)
        return list(frozenset(records_list))

   
    @staticmethod
    def get_all_groups(user_id):
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            groups = map(lambda x: x.group, student.records.filter(status="1"))
        except Student.DoesNotExist:
             logger.error('Function Student.get_all_groups(user_id = %d) throws Student.DoesNotExist exception.' % user_id )
             raise NonStudentException()
        return groups
    
    @staticmethod
    def get_schedule(user_id):
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            groups = [g for g in Student.get_all_groups(user_id) if g.subject.semester.is_current_semester()]
            subjects = set([group.subject for group in groups])
            for group in groups:
                group.terms_ = group.get_all_terms()
                group.subject_ = group.subject
            return groups
        except Student.DoesNotExist:
             logger.error('Function Student.get_schedule(user_id = %d) throws Student.DoesNotExist exception.' % user_id )
             raise NonStudentException()
         
    @staticmethod
    def records_block(user_id):
        user = User.objects.get(id=user_id)
        try :
            student = user.student
            if student.block == False:
                student.block = True
                student.save()
                return student
            else :
                return False
        except Student.DoesNotExist:
             logger.error('Function Student.records_block(user_id = %d) throws Student.DoesNotExist exception.' % user_id )
             raise NonStudentException()
    @staticmethod
    def records_unblock(user_id):
        user = User.objects.get(id=user_id)
        try :
            student = user.student
            if student.block == True:
                student.block = False
                student.save()
                return student
            else :
                return False
        except Student.DoesNotExist:
             logger.error('Function Student.records_unblock(user_id = %d) throws Student.DoesNotExist exception.' % user_id )
             raise NonStudentException()
 

    @staticmethod
    def get_zamawiany(user_id):
        try:
            user = User.objects.get(id=user_id)
            student = Student.objects.get(user=user)
            zamawiany = StudiaZamawiane.objects.get(student=student)
            return zamawiany
        except (User.DoesNotExist, Student.DoesNotExist, StudiaZamawiane.DoesNotExist):
             return None
        
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
