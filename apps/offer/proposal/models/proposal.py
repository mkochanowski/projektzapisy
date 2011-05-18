# -*- coding: utf-8 -*-

"""
    Proposal of course
"""

from datetime import datetime

from django.db                  import models
from django.contrib.auth.models import User

from apps.offer.proposal.exceptions import NonStudentException, NonEmployeeException

import re

from apps.offer.proposal.models.proposal_tag import ProposalTag
from apps.users.models                       import Employee, Student

class Proposal( models.Model ):
    """
        Proposal of course
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

    def entry_date(self):
        """
            Get date of first "description" - when this proposal was entered.
        """
        return self.descriptions.filter(deleted=False).order_by('date').values('date')[0]['date']

    def is_new(self):
        """
            Is true, when proposal is newer than half of year.
        """
        diff = (datetime.now() - self.entry_date())
        return diff.days < 30 * 6

    def is_in_group(self, user, group):
        """
            Is true when user is in group.
            Possible groups:
            fans
            teachers
            helpers
        """

        try:
            if group == 'fans':
                if self.fans.get(id=user.id):
                    return True
                return False
            elif group == 'teachers':
                if self.teachers.get(id = user.id):
                    return True
                return False
            elif group == 'helpers':
                if self.helpers.get(id = user.id):
                    return True
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
        
    def has_tag( self, tag_name ):
        """
            Checks if proposal has specified tag
        """
        for tag in self.tags.all():
            if tag.__unicode__() == tag_name:
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
            Checks if course is in offer
            (if it has tag offer)
        """
        return self.has_tag('offer')
    
    def in_summer( self ):
        """
            Checks if course is in summer semester
            (if it has tag summer)
        """
        return self.has_tag('summer')
        
    def in_winter( self ):
        """
            Checks if course is in winter semester
            (if it has tag winter)
        """
        return self.has_tag('winter')
        
    def is_exam( self ):
        """
            Checks if proposal has exam
            (if it has tag exam)
        """               
        return self.has_tag('exam')
        
    def in_english( self ):
        """
            Checks if classes in english are possible
            (if it has tag english)
        """
        return self.has_tag('english')

    @staticmethod
    def get_offer():
        return Proposal.objects.filter(tags__name='offer').values_list('pk', flat=True)

    @staticmethod
    def get_vote():
        return Proposal.objects.filter(tags__name='vote').values_list('pk', flat=True)