# -*- coding: utf-8 -*-

from django import template
from django.utils.safestring  import mark_safe
from libs import postmarkup
import logging

register = template.Library()
logger = logging.getLogger()

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

# filter checks url validity, and:
# - if it's ok (modulo "http://" prefix) - returns it
# - in the other case - returns "/" and logs it
@register.filter
def validate_url(str):
	from django.core.validators import URLValidator, ValidationError
	from StringIO import StringIO
	import traceback
	import string
	validate = URLValidator(verify_exists=False)
	try:
		validate(str)
	except ValidationError:
		try:
			validate('http://' + str)
			str = 'http://' + str
		except ValidationError:
			trace = StringIO()
			traceback.print_stack(file=trace)
			trace = trace.getvalue().split('\n')
			trace = filter(lambda str: str.find('html') >= 0, trace)
			trace = string.join(trace, '\n')
			logger.warning('Invalid URL couldn\'t be displayed in template: '
				+ str + '\n' + trace)
			return '/'
	return str

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

@register.filter
def safestring( str ):
    return mark_safe( str )
