# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger()

# klasa zapisująca nie przechwycone wyjątki do logu
class ErrorHandlerMiddleware(object):

	def process_exception(self, request, exception):
		# jeżeli będzie potrzeba pobrania dokładniejszych informacji o wyjątku:
		# sys.exc_info()
		# traceback.print_tb()
		logger.exception('Unhandled exception')
