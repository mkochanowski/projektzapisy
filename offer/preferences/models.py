# -*- coding:utf-8 -*-

from django.db import models

from users.models import Employee
from offer.proposal.models import Proposal
from offer.preferences.exceptions import *

PREFERENCE_CHOICES = (
    (3, 'Chętnie'),
    (2, 'Być może'),
    (1, 'Raczej nie'),
    (0, 'Nie'),
)

class PreferenceManager(models.Manager):
    def get_employees_prefs(self, employee, hidden=None, types=None, query=None):
        """
        Returns employee's preferences.

        hidden - include hidden
        types  - accepted type of the related proposal
        q      - substring of the related proposal's name
        """
        prefs = Preference.objects.filter(
            employee=employee)
        if not hidden:
            prefs = prefs.exclude(hidden=True)
        if types:
            prefs = prefs.filter(proposal__type__in=types)
        if query: # TODO: zaawansowane filtrowanie
            prefs = prefs.filter(proposal__name__icontains=query)
        return prefs

    def init_preference(self, employee, course):
        """
        Sets initial values for employee's preferences with regard
        to the given course.
        """
        try:
            Preference.objects.get(employee=employee, proposal=course)
            raise CoursePreferencesAlreadySet
        except Preference.DoesNotExist:
            pref = Preference(
                employee = employee,
                proposal = course,
                hidden   = False,
                lecture  = 0,
                review_lecture = 0,
                tutorial = 0,
                lab      = 0)
            pref.save()
            return pref

class Preference(models.Model):
    """
    A model representing employee's will to give lectures and tutor
    for a course.
    """
    employee   = models.ForeignKey(Employee, verbose_name='pracownik')
    proposal   = models.ForeignKey(Proposal, verbose_name='przedmiot')
    hidden     = models.BooleanField(default=False, 
                                     verbose_name='ukryte')
    
    # preferences
    lecture    = models.IntegerField(choices=PREFERENCE_CHOICES, 
                                     verbose_name='wykład')
    review_lecture = models.IntegerField(choices=PREFERENCE_CHOICES, 
                                     verbose_name='repetytorium')
    tutorial   = models.IntegerField(choices=PREFERENCE_CHOICES, 
                                     verbose_name='ćwiczenia')
    lab        = models.IntegerField(choices=PREFERENCE_CHOICES, 
                                     verbose_name='pracownia')
    
    objects = PreferenceManager()
    
    class Meta:
        verbose_name = 'preferencja'
        verbose_name_plural = 'preferencje'
    
    def __unicode__(self):
        rep = ''.join([self.employee.user.get_full_name(),
                       ': ',
                       self.proposal.name])
        return rep
    
    def hide(self):
        """
        Hides this preference in a default employee's view.
        """
        self.hidden = True
        self.save()
    
    def unhide(self):
        """
        Unhides this preference in a default employee's view.
        """
        self.hidden = False
        self.save()
    
    def set_preference(self, **kwargs):
        """
        Sets employee's preferences.

        Example usage:
        p.set_preference(lecture=2, tutorial=0)

        Values are restricted with PREFERENCE_CHOICES.
        """
        valid_prefs = ['lecture', 'review_lecture', 'tutorial', 'lab']
        valid_values = dict(PREFERENCE_CHOICES).keys()
        for pref in filter(valid_prefs.__contains__, kwargs.keys()):
            if kwargs[pref] not in valid_values:
                raise UnknownPreferenceValue
            self.__setattr__(pref, kwargs[pref])
        self.save()
                       
