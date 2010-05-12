# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import *

from offer.proposal.exceptions import *

import re

from proposal_tag import ProposalTag
from users.models import Employee, Student
          
PROPOSAL_TYPES = (
    ('seminar', 'Seminarium'),
    ('course', 'Kurs'),
)

PROPOSAL_HOURS = (
    (0, 0),
    (15, 15),
    (30, 30),
    (45, 45),
    (60, 60),
)

class Proposal( models.Model ):
    name = models.CharField(max_length = 255,
                            verbose_name = 'nazwa przedmiotu' )
    slug = models.SlugField(max_length = 255,
                            unique = True, verbose_name='odnośnik' )
    tags     = models.ManyToManyField(ProposalTag)
    fans     = models.ManyToManyField(Student, verbose_name='poszli by na to')
    teachers = models.ManyToManyField(Employee, verbose_name='poprowadziliby to')
    tags = models.ManyToManyField(ProposalTag, blank = True)
    type = models.CharField(max_length = 30, choices = PROPOSAL_TYPES, 
        verbose_name = 'typ')
    ects = models.IntegerField(verbose_name ='sugerowana liczba punktów ECTS')
    lectures = models.IntegerField(verbose_name='ilość godzin wykładów', 
        choices = PROPOSAL_HOURS)
    repetitories = models.IntegerField(verbose_name='ilość godzin repetytoriów', 
        choices = PROPOSAL_HOURS)
    exercises = models.IntegerField(verbose_name='ilość godzin ćwiczeń', 
        choices = PROPOSAL_HOURS)
    laboratories = models.IntegerField(verbose_name='ilość godzin pracowni', 
        choices = PROPOSAL_HOURS)
                
    class Meta:
        verbose_name = 'przedmiot'
        verbose_name_plural = 'przedmioty'
        app_label = 'proposal'
    
    def description(self):
        """
            Get last description.
        """
        if self.descriptions.count() > 0:
            return self.descriptions.order_by('-date')[0]
        else:
            return None            

    def isFan(self, user):
        try:
            if self.fans.get(user = user):
                return True
            else:
                return False
        except Student.DoesNotExist:
            return False
            
    def isTeacher(self, user):
        try:
            if self.teachers.get(user = user):
                return true
            else:
                return false
        except Employee.DoesNotExist:
            return False            
    def addUserToFans(self, user):
        try:
            student = user.student
            self.fans.add(student)
            self.save()
        except Student.DoesNotExist:
            raise NonStudentException()

    def deleteUserFromFans(self, user):
        try:
            student = user.student
            self.fans.remove(student)
            self.save()
        except Student.DoesNotExist:
            raise NonStudentException()
            
    def addUserToTeachers(self, user):
        try:
            teacher = user.employee
            self.teachers.add(teacher)
            self.save()
        except Employee.DoesNotExist:
            raise NonEmployeeException()

    def deleteUserToTeachers(self, user):
        try:
            teacher = user.employee
            self.teachers.remove(teacher)
            self.save()
        except Employee.DoesNotExist:
            raise NonEmployeeException()
                
    def fansCount(self):
        return self.fans.all().count()
        
    def teachersCount(self):
        return self.teachers.all().count()
    
    def __unicode__(self):
        return self.name
        
    def createSlug(self, name):
        slug = name.lower()
        slug = re.sub(u'ą', "a", slug)
        slug = re.sub(u'ę', "e", slug)
        slug = re.sub(u'ś', "s", slug)
        slug = re.sub(u'ć', "c", slug)
        slug = re.sub(u'ż', "z", slug)
        slug = re.sub(u'ź', "z", slug)
        slug = re.sub(u'ł', "l", slug)
        slug = re.sub(u'ó', "o", slug)
        slug = re.sub(u'ć', "c", slug)
        slug = re.sub(u'ń', "n", slug)
        slug = re.sub("\W", "-", slug)
        slug = re.sub("-+", "-", slug)
        slug = re.sub("^-", "", slug)
        slug = re.sub("-$", "", slug)
        return slug

    def in_summer( self ):
        # sprawdza czy przedmiot będzie w semestrze letnim
        # odpowiada za to tag summer
        for t in self.tags.all():
            if t.__unicode__() == 'summer':
                return True
        return False
    
    def in_winter( self ):
        # sprawdza czy przedmiot będzie w semestrze zimowym
        # odpowiada za to tag winter
        for t in self.tags.all():
            if t.__unicode__() == 'winter':
                return True
        return False
    
    @staticmethod
    def get_by_tag(tag):
        "Return proposals by tag."
        return Proposal.objects.filter(tags__name=tag)

    def inOffer(self):
        for t in self.tags.all():
            if t.__unicode__() == 'offer':
                return True
        return False