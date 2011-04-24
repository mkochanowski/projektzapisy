# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse

def prepare_ajax_students_list(students):
    return map(lambda s:
           {'id':       s.id,
            'album':    s.matricula,
            'recorded': s.recorded,
            'email':    s.user.email,
            'name':     u'%s %s' % (s.user.first_name, s.user.last_name),
            'link':     reverse('student-profile', args=[s.id])}, students)