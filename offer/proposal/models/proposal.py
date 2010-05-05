# -*- coding: utf-8 -*-

from django.db import models
import re

from proposal_tag import ProposalTag

class Proposal( models.Model ):
    name = models.CharField(max_length = 255,
                            verbose_name = 'nazwa przedmiotu' )
    slug = models.SlugField(max_length = 255,
                            unique = True, verbose_name='odnośnik' )
    tags = models.ManyToManyField(ProposalTag, blank = True)
    
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
    
    @staticmethod
    def get_by_tag(tag):
        "Return proposals by tag."
        return Proposal.objects.filter(tags__name=tag)
