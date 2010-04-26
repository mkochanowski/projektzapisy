# -*- coding: utf8 -*-

from django.db import models
import re

class Proposal( models.Model ):
    name = models.CharField( max_length = 255, verbose_name = 'nazwa przedmiotu' )
    slug = models.SlugField( max_length = 255, unique = True, verbose_name='odnośnik' )
    
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
