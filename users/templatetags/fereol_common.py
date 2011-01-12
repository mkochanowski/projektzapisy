# -*- coding: utf-8 -*-

from django import template
from libs import postmarkup

register = template.Library()

@register.filter
def bbcode(str):
    markup = postmarkup.PostMarkup()

    markup.add_tag(postmarkup.SimpleTag, u'b', u'strong')
    markup.add_tag(postmarkup.SimpleTag, u'i', u'em')
    markup.add_tag(postmarkup.SimpleTag, u'u', u'u')
    markup.add_tag(postmarkup.SimpleTag, u's', u's')

    return markup.render_to_html(str)

@register.filter
def nl2br(str):
    return str.replace("\n", "<br />")

@register.tag(name='captureas')
def do_captureas(parser, token):
    '''
        Dumps its contents into a context variable.

        Parameter: variable name

        Example use:
        {% captureas examplevar %}{% url exampleurl %}{% endcaptureas %}
        URL: {{ examplevar }}

        Source: http://djangosnippets.org/snippets/545/
    '''
    try:
        tag_name, args = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("'captureas' node requires a variable name.")
    nodelist = parser.parse(('endcaptureas',))
    parser.delete_first_token()
    return CaptureasNode(nodelist, args)

class CaptureasNode(template.Node):
    def __init__(self, nodelist, varname):
        self.nodelist = nodelist
        self.varname = varname

    def render(self, context):
        output = self.nodelist.render(context)
        context[self.varname] = output
        return ''
