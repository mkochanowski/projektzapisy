# -*- coding: utf-8 -*-
from apps.utils.fullcalendar import FullCalendarAdapter

__author__ = 'maciek'

class EventAdapter(FullCalendarAdapter):

    def get_backgroundColor(self, item):

        if not item.event.visible:
            return "#D06B64"

        if item.event.type in ['0', '1']:
            return "#7BD148"

        if item.event.type == '2':
            return "#B3DC6C"

        return None

    def get_borderColor(self, item):

        if not item.event.visible:
            return "#924420"


        if item.event.type in ['0', '1']:
            return "#7BD148"

        if item.event.type == '2':
            return "#93C00B"

        return None

    def get_title(self, item):

        if not item.event.visible and not self.request.user.has_perm('schedule.manage_events'):
            return u"Sala zajęta"

        if item.event.type in ['0', '1']:
            return str(item.event.course) + " " + str(item.event.get_type_display())

        return super(EventAdapter, self).get_title(item)

    def get_url(self, item):
        if not item.event.visible and not self.request.user.has_perm('schedule.manage_events'):
            return None

        return super(EventAdapter, self).get_url(item)

