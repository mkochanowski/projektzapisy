# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from fereol.users.models import Employee

class Subject( models.Model ):
    
    name = models.CharField( max_length = 255, verbose_name = 'nazwa przedmiotu' )
    slug = models.SlugField( max_length=255, unique = True, verbose_name='odnośnik' )
    #description = models.TextField( verbose_name = 'opis' ) # description should be in other model (for history)
    lectures = models.IntegerField( verbose_name = 'ilość godzin wykładów' )
    exercises = models.IntegerField( verbose_name = 'ilość godzin ćwiczeń' )
    laboratories = models.IntegerField( verbose_name = 'ilość godzin pracowni' )
    
    class Meta:
        verbose_name = 'przedmiot'
        verbose_name_plural = 'przedmioty'
    
    def description(self):
        """
            Get last description.
        """
        if self.descriptions.count() > 0:
            return self.descriptions.order_by('-date')[0]
        else:
            return None

    def __unicode__(self):
        return self.name

class SubjectDescription(models.Model):
    subject = models.ForeignKey(Subject, related_name = 'descriptions')
    description = models.TextField( verbose_name = 'opis' )
    date = models.DateTimeField(verbose_name = 'data dodania')

    class Meta:
        verbose_name = 'opis przedmiotu'
        verbose_name_plural = 'opisy przedmiotu'

    def __str__(self):
        return self.description

    def __unicode__(self):
        return self.description

#moved to PrettyLabel class in order to avoid code redundancy

#GROUP_TYPE_CHOICES = [ ( '1', u'wykład' ), ( '2', u'ćwiczenia' ), ( '3', u'pracownia' ) ]

#def group_type( code_type ):
   # """returns name of group type"""
   # dic = {}
  #  for key, value in GROUP_TYPE_CHOICES:
  #      dic[ key ] = value
  #  return dic[ code_type ]


class Classroom( models.Model ):
    """classroom in institute"""
    number = models.CharField( max_length = 4, verbose_name = 'numer sali' )
    
    class Meta:
        verbose_name = 'sala'
        verbose_name_plural = 'sale'
    
    def __unicode__(self):
        return self.number



GROUP_TYPE_CHOICES = [ ( '1', u'wykład' ), ( '2', u'ćwiczenia' ), ( '3', u'pracownia' ) ]

DAYS_OF_WEEK = [( '1', u'poniedziałek' ), ( '2', u'wtorek' ), ( '3', u'środa' ), ( '4', u'czwartek'), ( '5', u'piątek'), ( '6', u'sobota'), ( '7', u'niedziela')]

HOURS = [( '8', '8.00' ), ( '9', '9.00' ), ( '10', '10.00' ), ( '11', '11.00' ), ( '12', '12.00' ), ( '13', '13.00' ), ( '14', '14.00' ), ( '15', '15.00' ), 
         ( '16', '16.00' ), ( '17', '17.00' ), ( '17', '17.00' ), ( '18', '18.00' ), ( '19', '19.00' ), ( '20', '20.00' ), ( '21', '21.00' ), ( '22', '22.00' )]
 
 
class PrettyLabel:
   
   @staticmethod
   def encode_list(code_id, list):
      """encodes list od tuples"""
      dic = {}
      for key, value in list:
         dic[ key ] = value
      return dic[ code_id ]

  
class Term( models.Model ):
   
    """terms of groups"""
    dayOfWeek = models.CharField( max_length = 1, choices = DAYS_OF_WEEK, verbose_name = 'dzień tygodnia') 
    hourFrom = models.CharField(max_length = 2, choices = HOURS, verbose_name = 'od')
    hourTo = models.CharField(max_length = 2, choices = HOURS, verbose_name = 'do')

    class Meta:
        verbose_name = 'termin'
        verbose_name_plural = 'terminy'

    def __unicode__(self):
        return PrettyLabel.encode_list(self.dayOfWeek, DAYS_OF_WEEK) + ', (od: ' + PrettyLabel.encode_list(self.hourFrom, HOURS) + ', do: ' + PrettyLabel.encode_list(self.hourTo, HOURS) + ')'

    
class Group( models.Model ):
    """group for subject"""
    subject = models.ForeignKey( Subject, verbose_name = 'przedmiot' )
    teacher = models.ForeignKey( Employee, verbose_name = 'prowadzący' )
    type = models.CharField( max_length = 1, choices = GROUP_TYPE_CHOICES, verbose_name = 'typ zajęć' )
    classroom = models.ManyToManyField( Classroom, verbose_name = 'sala', related_name = 'grupy' )
    term = models.ManyToManyField( Term, verbose_name = 'termin zajęć', related_name = 'grupy')
    limit = models.PositiveSmallIntegerField( default = 0, verbose_name = 'limit miejsc')
    
    def get_teacher_full_name(self):
        """returns teacher's full name for group"""
        return self.teacher.user.get_full_name()

    def get_all_terms(self):
        """return all terms of current groupt""" 
        return self.term.all()

    # poprawka kodu Pawła (Zasada o ktorej czym wspominal Jan ;-) )
    def get_all_classrooms(self):
        """return all classrooms of current groupt""" 
        return self.classroom.all()

    def get_group_limit(self):
        """return maximal amount of participants"""
        return self.limit

    def subject_slug(self):
        return self.subject.slug


    class Meta:
        verbose_name = 'grupa'
        verbose_name_plural = 'grupy'

    def __unicode__(self):
        return self.subject.name + ': ' + PrettyLabel.encode_list( self.type, GROUP_TYPE_CHOICES )

class Books( models.Model ):
    subject = models.ForeignKey(Subject, verbose_name = 'przedmiot')
    name = models.TextField( verbose_name = 'nazwa' )
    
    class Meta:
        verbose_name = 'książka'
        verbose_name_plural = 'książki'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name
