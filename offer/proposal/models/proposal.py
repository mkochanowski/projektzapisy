# -*- coding: utf-8 -*-

"""
    Proposal of subject
"""

from django.db                  import models
from django.contrib.auth.models import User

from offer.proposal.exceptions import NonStudentException, NonEmployeeException

import re

from offer.proposal.models.proposal_tag import ProposalTag
from users.models                       import Employee, Student

class Proposal( models.Model ):
    """
        Proposal of subject
    """
    name = models.CharField(max_length = 255,
                            verbose_name = 'nazwa przedmiotu' )
    slug = models.SlugField(max_length = 255,
                            unique = True, verbose_name='odnośnik' )
    fans     = models.ManyToManyField('users.Student', blank=True, 
                                      verbose_name='poszli by na to')
    teachers = models.ManyToManyField('users.Employee', blank=True, related_name='proposal_teachers_related',
                                      verbose_name='poprowadziliby to')
    helpers = models.ManyToManyField('users.Employee', blank=True,  related_name='proposal_helpers_related',
                                      verbose_name='pomogliby poprowadzić to')
    tags = models.ManyToManyField(ProposalTag, blank = True)
    owner = models.ForeignKey(User, related_name='wlasciciel', verbose_name='wlasciciel', null = True, blank=True)
    deleted = models.BooleanField(default=False, verbose_name="usuniety")
                
    class Meta:
        verbose_name = 'przedmiot'
        verbose_name_plural = 'przedmioty'
        app_label = 'proposal'
        permissions = (
            ("can_create_offer", u"Może tworzyć ofertę dydaktyczną"),
            ("can_delete_proposal", u"Może usuwać propozycje"),
        )
    
    def description(self):
        """
            Get last description.
        """
        if self.descriptions.filter(deleted=False).count() > 0:
            return self.descriptions.filter(deleted=False).order_by('-date')[0]
        else:
            return None            

    def is_in_group(self, user, group):
        """
            Is true when user is in group.
            Possible groups:
            fans
            teachers
            helpers
        """
        if group == 'fans':
            field = self.fans
        elif group == 'teachers':
            field = self.teachers
        elif group == 'helpers':
            field = self.helpers

        try:
            if field.get(user = user):
                return True
            else:
                return False
        except Student.DoesNotExist:
            return False
        except Employee.DoesNotExist:
            return False            
            
    def add_user_to_group(self, user, group):
        """
            Add user to group
            Possible group:
            fans
            teachers
            helpers
        """
        try:
            if group == 'fans':
                field = self.fans
                person = user.student
            elif group == 'teachers':
                field = self.teachers
                person = user.employee
            elif group == 'helpers':
                field = self.helpers
                person = user.employee
            field.add(person)
            self.save()
        except Student.DoesNotExist:
            raise NonStudentException()
        except Employee.DoesNotExist:
            raise NonEmployeeException()

    def delete_user_from_group(self, user, group):
        """
            Delete user from group
            Possible group:
            fans
            teachers
            helpers
        """
        try:
            if group == 'fans':
                field = self.fans
                person = user.student
            elif group == 'teachers':
                field = self.teachers
                person = user.employee
            elif group == 'helpers':
                field = self.helpers
                person = user.employee
            field.remove(person)
            self.save()
        except Student.DoesNotExist:
            raise NonStudentException()
        except Employee.DoesNotExist:
            raise NonEmployeeException()            
                
    def fans_count(self):
        """
            Count fans
        """
        return self.fans.all().count()
        
    def teachers_count(self):
        """
            Count teachers
        """
        return self.teachers.all().count()
        
    def helpers_count(self):
        """
            Count helpers
        """
        return self.helpers.all().count()
    
    def __unicode__(self):
        return self.name
  
    def create_slug(self, name):
        """
            Creates slug
        """
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
        """
            Checks if subject is in summer semester
            (if it has tag summer)
        """
        for tag in self.tags.all():
            if tag.__unicode__() == 'summer':
                return True
        return False
    
    def in_winter( self ):
        """
            Checks if subject is in winter semester
            (if it has tag winter)
        """
        for tag in self.tags.all():
            if tag.__unicode__() == 'winter':
                return True
        return False
    
    @staticmethod
    def get_by_tag(tag_name):
        """
            Return proposals by tag.
        """
        return Proposal.objects.filter(tags__name=tag_name)
    
    def add_tag(self, tag_name):
        """
            Apply tag to the proposal
        """
        try:
            tag = ProposalTag.objects.get(name=tag_name) 
        except ProposalTag.DoesNotExist:
            tag = ProposalTag.objects.create(name=tag_name)
        finally:
            self.tags.add(tag)
    
    def remove_tag(self, tag_name):
        """
            Remove tag from the proposal.
        """
        try:
            tag = ProposalTag.objects.get(name=tag_name)
            self.tags.remove(tag)
        except ProposalTag.DoesNotExist:
            pass

    def in_offer(self):
        """
            Checks if subject is in offer
            (if it has tag offer)
        """
        for tag in self.tags.all():
            if tag.__unicode__() == 'offer':
                return True
        return False
