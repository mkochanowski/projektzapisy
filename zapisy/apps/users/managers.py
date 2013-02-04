# -*- coding: utf-8 -*-


from django.db import models
from django.db.models.aggregates import Min


class GettersManager(models.Manager):

    def filter_with_t0(self, *args, **kwargs):
        return self.get_query_set().filter(*args, **kwargs).only('user__first_name',
                             'user__last_name', 'matricula', 'ects').annotate(t0_min=Min('opening_times__opening_time'))


    def get_list_full_info(self, begin='All'):
        def next_char(begin):
            try:
                return chr(ord(begin) + 1)
            except ValueError:
                return chr(90)

        if begin == 'Z':
            return self.filter_with_t0(status=0,user__last_name__gte=begin).\
                    select_related().order_by('user__last_name', 'user__first_name')
        elif begin == 'All':
            return self.filter_with_t0(status=0).\
                    select_related().order_by('user__last_name', 'user__first_name')
        else:
            end = next_char(begin)
            return self.filter_with_t0(status=0,user__last_name__range=(begin, end)).\
                    select_related().order_by('user__last_name', 'user__first_name')

