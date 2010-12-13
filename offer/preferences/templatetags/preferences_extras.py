# -*- coding: utf-8 -*-

from django.template import Library, Node, TemplateSyntaxError, \
     Variable, VariableDoesNotExist

register = Library()

from offer.preferences.models import PREFERENCE_CHOICES

class PrefsFormOptions(Node):
    """Return a list of <options> given selected"""
    def __init__(self, selected):
        self.selected = Variable(selected)
    
    def render(self, context):
        try:
            text = ''
            selected = self.selected.resolve(context)
            for (val, name) in PREFERENCE_CHOICES:
                if selected == val:
                    text += '<option selected="selected"' \
                            'value="%s">%s</option>' % (val, name)
                else:
                    text += '<option value="%s">%s</option>' % (val, name)
        except VariableDoesNotExist:
            pass
        return text

@register.tag
def prefs_form_options(parser, token):
    bits = token.contents.split()
    if len(bits) == 3:
        if bits[1] != 'selected':
            raise TemplateSyntaxError, "first argument to the prefs_form_options tag must be 'selected'"
        return PrefsFormOptions(bits[2])
    if len(bits) == 1:
        return PrefsFormOptions("0")
    raise TemplateSyntaxError, "prefs_form_options tag takes zero or two arguments"

