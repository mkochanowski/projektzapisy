# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User, UserManager
from django.core.mail import send_mail
from django.db.models.loading import cache
from django.template import Context
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError
from apps.users.exceptions import NonEmployeeException, NonStudentException
from apps.enrollment.courses.models.points import PointTypes
from apps.enrollment.courses.models import Semester
from apps.enrollment.courses.models import StudentOptions
from django.db.models.signals import post_save
import datetime

from fereol import settings

import logging
logger = logging.getLogger()

EMPLOYEE_STATUS_CHOICES = [(0, 'aktywny'), (1, 'nieaktywny')]

class Related(models.Manager):
    def get_query_set(self):
        return super(Related, self).get_query_set().select_related('user')

class ExtendedUser(User):    
    is_student = models.BooleanField(default = False, verbose_name="czy student?")
    is_employee = models.BooleanField(default = False, verbose_name="czy pracownik?")
    is_zamawiany = models.BooleanField(default = False, verbose_name="czy zamawiany?")

    objects = UserManager()
    
    class Meta:
        verbose_name = 'użutkownik'
        verbose_name_plural = 'użytkownicy'

class UserProfile(models.Model):
    # This field is required.
    user         = models.OneToOneField(User, related_name='_profile_cache')
    is_student   = models.BooleanField(default = False, verbose_name="czy student?")
    is_employee  = models.BooleanField(default = False, verbose_name="czy pracownik?")
    is_zamawiany = models.BooleanField(default = False, verbose_name="czy zamawiany?")

class BaseUser(models.Model):
    '''
    User abstract class. For every app user there is entry in django.auth.
    We do not inherit after User directly, because of problems with logging beckend etc.
    '''
    receive_mass_mail_enrollment = models.BooleanField(
        default = True, 
        verbose_name="otrzymuje mailem ogłoszenia Zapisów")
    receive_mass_mail_offer = models.BooleanField(
        default = True, 
        verbose_name="otrzymuje mailem ogłoszenia OD")
    receive_mass_mail_grade = models.BooleanField(
        default = True, 
        verbose_name="otrzymuje mailem ogłoszenia Oceny Zajęć")
    last_news_view = models.DateTimeField(default=datetime.datetime.now())
    
    objects = Related()

    def get_full_name(self):
        return self.user.get_full_name()
    get_full_name.short_description = 'Użytkownik'

    def get_number_of_news(self):
        from apps.news.models import News
        news = News.objects.exclude(category='-').filter(date__gte=self.last_news_view)
        count_news = len(news)
        return count_news

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
        return hasattr(user, "student") and user.student

    @staticmethod
    def is_employee(user):
        return hasattr(user, "employee") and user.employee

    def __unicode__(self):
        return self.get_full_name
    
    class Meta:
        abstract = True



class Employee(BaseUser):
    '''
    Employee.
    '''

    user = models.OneToOneField(User, verbose_name="Użytkownik", related_name='employee')
    consultations = models.TextField(verbose_name="konsultacje", null=True, blank=True)
    homepage = models.URLField(verify_exists=True, verbose_name='strona domowa', default="", null=True, blank=True)
    room = models.CharField(max_length=20, verbose_name="pokój", null=True, blank=True)
    status = models.PositiveIntegerField(default=0, choices=EMPLOYEE_STATUS_CHOICES, verbose_name="Status")
        
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

    def get_sex(self):
        if self.user.first_name[-1] == 'a':
            return 'K'
        else:
            return 'M'

    @staticmethod
    def get_actives():
        return Employee.objects.filter(user__is_active=True).order_by('user__last_name', 'user__first_name'). extra(
                        where=["(SELECT COUNT(*) FROM courses_courseentity WHERE courses_courseentity.owner_id=users_employee.id)>0"]
        )


    @staticmethod
    def get_list(begin):
        def next_char(begin):
            try:
                return chr(ord(begin) + 1)
            except ValueError:
                return chr(90)
        if begin == 'Z':
            return Employee.objects.filter(user__last_name__gte=begin, status=0).\
                    select_related().order_by('user__last_name', 'user__first_name')
        elif begin == 'All':
            return Employee.objects.filter(status=0).\
                    select_related().order_by('user__last_name', 'user__first_name')
        else:
            end = next_char(begin)
            return Employee.objects.filter(user__last_name__range=(begin, end), status=0).\
                    select_related().order_by('user__last_name', 'user__first_name')




    @staticmethod
    def get_all_groups_in_semester(user_id):
        from apps.enrollment.courses.models import Group, Semester

        user = User.objects.get(id=user_id)
        semester = Semester.get_default_semester()
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
        ordering = ['user__last_name', 'user__first_name']
      
    def __unicode__(self):
        return unicode(self.user.get_full_name())

class Student(BaseUser):
    ''' 
    Student.
    '''

    user = models.OneToOneField(User, verbose_name="Użytkownik", related_name='student')
    matricula = models.CharField(max_length=20, default="", unique=True, verbose_name="Numer indeksu")
    ects = models.PositiveIntegerField(verbose_name="punkty ECTS", default=0)
    records_opening_bonus_minutes = models.PositiveIntegerField(default=0, verbose_name="Przyspieszenie otwarcia zapisów (minuty)")
    program = models.ForeignKey('Program', verbose_name='Program Studiów', null=True, default=None)
    block = models.BooleanField(verbose_name="blokada planu", default = False)
    semestr = models.PositiveIntegerField(default=0, verbose_name="Semestr")
    status = models.PositiveIntegerField(default=0, verbose_name="Status")
    status.help_text = "0 - aktywny student, 1 - skreślony student"

    
    def is_active(self):
        return self.status == 0

    def get_sex(self):
        if self.user.first_name[-1] == 'a':
            return 'K'
        else:
            return 'M'

    def get_type_of_studies(self):
        """ returns type of studies """
        semestr = {1:'pierwszy',2:'drugi',3:'trzeci',4:'czwarty',5:'piąty',6:'szósty',7:'siódmy',8:'ósmy',9:'dziewiąty',10:'dziesiąty',0:'niezdefiniowany'}[self.semestr]
        return '%s, semestr %s' % (self.program , semestr)
    get_type_of_studies.short_description = 'Studia'

    def participated_in_last_grades(self):
        from apps.grade.ticket_create.models.student_graded import StudentGraded
        return StudentGraded.objects.filter(student=self, semester__in=[41, 42]).count()

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

    def get_voted_courses(self, given_points):
        """ returns courses which were voted with given_points by student """
        current_semester = Semester.get_default_semester()
        from apps.offer.vote.models.single_vote import SingleVote
        return map(lambda x: x.course, SingleVote.objects.filter(student=self, state__semester_summer=current_semester, correction=given_points).select_related('course').order_by('course__name'))
        #return map(lambda x: x.course, StudentOptions.objects.filter(course__semester__id__exact=current_semester.id).filter(student=self, records_opening_bonus_minutes=minutes).order_by('course__name'))
        
    def get_records_history(self,default_semester=None):
        '''
        Returns list of ids of course s that student was enrolled for.
        '''
        if not default_semester:
            from apps.enrollment.courses.models import Semester
            default_semester = Semester.get_default_semester()
        records = self.records.exclude(group__course__semester = \
            default_semester).select_related('group', 'group__course',
            'group__course__entity')
        records_list = map(lambda x: x.group.course.entity.id, records)
        return list(frozenset(records_list))


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
            default_semester = Semester.get_default_semester()
            groups = [g for g in Student.get_all_groups(student) \
                if g.course.semester == default_semester] #TODO: nieoptymalnie
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

    #TODO: to NIE MA być pole statyczne - najlepiej zrobić mapę (pole statyczne)
    is_zamawiany_cache = None
    def is_zamawiany(self):
        if not (self.is_zamawiany_cache is None):
            return self.is_zamawiany_cache
        try:
            self.zamawiany()
            self.is_zamawiany_cache = True
        except StudiaZamawiane.DoesNotExist:
            self.is_zamawiany_cache = False
        return self.is_zamawiany_cache

    def is_first_year_student(self):
        return (self.semestr in [1,2]) and (self.program.id in [0,2]) 

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
    student = models.OneToOneField(Student, related_name='zamawiane', verbose_name='Student')
    points =  models.FloatField(verbose_name='Punkty', null=True, blank=True)
    comments = models.TextField(verbose_name='Uwagi', blank=True, null=True)
    bank_account = models.CharField(max_length=40, null=True, blank=True, verbose_name="Numer konta bankowego")

    def save(self, *args, **kwargs):
        try:
            old_sz = StudiaZamawiane.objects.get(id=self.id)
            if self.bank_account != old_sz.bank_account and not (self.bank_account.lower()=='pl' and old_sz.bank_account==''):
                Site = cache.get_model('sites', 'Site')
                current_site = Site.objects.get_current()
                site_name, domain = current_site.name, current_site.domain
                subject = '[Fereol] Zmiana numeru konta bankowego'
                subject_employee = 'Zmiana numeru konta %s -> %s' % (self.student.matricula, self.bank_account and self.bank_account or '')
                c = {
                    'site_domain': domain,
                    'site_name': site_name.replace('\n',''),
                    'student': self.student,
                    'old_account' : old_sz.bank_account and old_sz.bank_account or '',
                    'new_account' : self.bank_account and self.bank_account or '',
                }
                context = Context(c)
                message_user = render_to_string('users/bank_account_change_email.html', context_instance=context)
                message_employee = render_to_string('users/bank_account_change_email_employee.html', context_instance=context) 
                
                emails = map( lambda x: x['email'], StudiaZamawianeMaileOpiekunow.objects.values())
                
                send_mail(subject, message_user, None, [self.student.user.email])
                send_mail(subject_employee, message_employee, None ,emails)
                logger.info('User_id %s student_id %s has changed his bank_account to \'%s\'' % (self.student.user.id, self.student.id, self.bank_account))
        except:
            pass     
        if self.bank_account=='':
            self.bank_account = None
        super(StudiaZamawiane, self).save(*args, **kwargs)

    def clean(self):
        self.bank_account = self.bank_account.upper().replace(' ', '')
        if not self.bank_account[:2].isalpha():
            self.bank_account = 'PL' + self.bank_account
        if not StudiaZamawiane.check_iban(self.bank_account):
            raise ValidationError('Podany numer konta nie jest poprawny')

    @staticmethod
    def _normalize_char(c):
        if c.isalpha():
            return str(ord(c.lower()) - ord('a') + 10)
        return c

    @staticmethod
    def check_iban(number):
        """Checks if given number is valid IBAN"""
        number = number.replace(' ', '')
        if number=='PL' or number=='' or number is None:
            return True
        lengths = {'pl': 28}
        if not number.isalnum():
            return False
        country_code = number[:2].lower()
        if not country_code.isalpha():
            number = 'pl' + number
            country_code = 'pl'
        valid_length = lengths.get(country_code)
        if valid_length is not None:
            if len(number) != valid_length:
                return False
        code = int(''.join(map(StudiaZamawiane._normalize_char, number[4:] + number[:4])))
        return code % 97 == 1            

    class Meta:
        verbose_name = 'Studia zamawiane'
        verbose_name_plural = 'Studia zamawiane'

    def __unicode__(self):
        return 'Student zamawiany: '+str(self.student).decode('utf-8')

class StudiaZamawianeMaileOpiekunow(models.Model):
    """
        Model przechowuje maile, na które są wysyłane maile o zmianie numeru konta bankowego studentów zamawianych
    """
    email = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = 'Studia zamawiane - opiekunowie'
        verbose_name_plural = 'Studia zamawiane - opiekunowie'
        
    def __unicode__(self):
        return self.email



# definition of UserProfile from above
# ...

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

#post_save.connect(create_user_profile, sender=User)
