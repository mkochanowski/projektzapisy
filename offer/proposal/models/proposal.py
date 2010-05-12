# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import *

from offer.proposal.exceptions import *

import re

from proposal_tag import ProposalTag
from users.models import Employee, Student

class Proposal( models.Model ):
    name = models.CharField(max_length = 255,
                            verbose_name = 'nazwa przedmiotu' )
    slug = models.SlugField(max_length = 255,
                            unique = True, verbose_name='odnośnik' )
    tags     = models.ManyToManyField(ProposalTag)
    fans     = models.ManyToManyField(Student, verbose_name='poszli by na to')
    teachers = models.ManyToManyField(Employee, verbose_name='poprowadziliby to')
    
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
        if self.teachers.objects.get(user = user):
            return true
        else:
            return false
            
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
    
    @staticmethod
    def get_by_tag(tag):
        "Return proposals by tag."
        return Proposal.objects.filter(tags__name=tag)
