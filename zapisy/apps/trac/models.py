# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.db.models.query_utils import Q
from django.utils.encoding import smart_unicode

class IssueManager(models.Manager):
    def get_query_set(self):
        return super(IssueManager, self).get_query_set().filter(deleted=False)

class Issue(models.Model):
    visibles = [(0, u'admini'), (1, u'dla pracowników'), (2, u'dla wszystkich')]
    types    = [(0, u'błąd'), (1, u'propozycja')]
    statuses = [(0, u'nowy'), (1, u'potrzebna decyzja'), (2, u'zaakceptowany'),
                (3, u'w toku'), (4, u'testy'), (5, u'zakończony'), (u'odrzucony')]

    author    = models.ForeignKey(User, related_name='created_issues')
    developer = models.ForeignKey(User, related_name='issues')
    visible = models.IntegerField(choices=visibles, default=0)
    type    = models.IntegerField(choices=types, null=True, blank=True)
    status  = models.IntegerField(choices=statuses, default=0)

    created = models.DateTimeField(auto_now_add=True)
    edited  = models.DateTimeField(auto_now=True)

    deleted = models.BooleanField(default=False)

    title = models.CharField(max_length=250)
    description = models.TextField()

    objects = IssueManager()

    class Meta:
        pass

    def __unicode__(self):
        return smart_unicode(self.title)

    def delete(self, using=None):
        self.deleted = True
        self.save(using=using)

    @staticmethod
    def visible_level(user):
        if user.is_staff():
            return 0
        if hasattr(user, 'employee'):
            return 1
        return 2

    @staticmethod
    def get_list_for_user(user):
        visible = Issue.visible_level(user)
        return Issue.objects.filter(Q(author=user) | Q(visible__gte=visible))

    @staticmethod
    def get_issue_for_user(id, user):
        visible = Issue.visible_level(user)
        return Issue.objects.get(Q(id=id), Q(author=user) | Q(visible__gte=visible))

