from apps.utils.fullcalendar import FullCalendarAdapter

__author__ = 'maciek'

class EventAdapter(FullCalendarAdapter):

    def get_backgroundColor(self, item):

        if not item.event.visible:
            return "#D06B64"

        if item.event.type in ['0', '1']:
            return "#FBE983"

        if item.event.type == '2':
            return "#B3DC6C"

        return None

    def get_borderColor(self, item):

        if not item.event.visible:
            return "#924420"


        if item.event.type in ['0', '1']:
            return "#BDB634"

        if item.event.type == '2':
            return "#93C00B"

        return None
