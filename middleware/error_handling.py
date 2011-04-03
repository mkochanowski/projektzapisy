# -*- coding: utf-8 -*-

from logging import getLogger
from django.http import HttpResponseNotAllowed
from django.template import RequestContext, loader

logger = getLogger()

# klasa zajmująca się błędami aplikacji
class ErrorHandlerMiddleware(object):

	def process_exception(self, request, exception):
		# logowanie nie przechwyconych wyjątków
		#
		# jeżeli będzie potrzeba pobrania dokładniejszych informacji o wyjątku:
		# sys.exc_info()
		# traceback.print_tb()
		logger.exception('Unhandled exception')

	def process_response(self, request, response):
		# obsługiwanie niestandardowych stron błędów
		if isinstance(response, HttpResponseNotAllowed):
			response.content = loader.render_to_string("405.html",
				context_instance=RequestContext(request))
		return response
