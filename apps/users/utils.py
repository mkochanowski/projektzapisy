# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse

def prepare_ajax_students_list(students):
    return map(lambda s:
           {'id':       s.user.id,
            'album':    s.matricula,
            'recorded': s.recorded,
            'email':    s.user.email,
            'name':     u'%s %s' % (s.user.first_name, s.user.last_name),
            'link':     reverse('student-profile', args=[s.user.id])}, students)

def prepare_ajax_employee_list(employees):
    return map(lambda e:
            { 'id':  e.user.id,
              'email': e.user.email,
              'name':     u'%s %s' % (e.user.first_name, e.user.last_name),
              'link': reverse('employee-profile', args=[e.user.id]),
              'short_old': e.short_old,
              'short_new': e.short_new},
            employees)