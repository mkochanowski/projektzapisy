# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect

class SubdomainMiddleware:
	 def process_request(self, request):
		domain = request.META.get('HTTP_HOST', '')
		#print request.session['no_mobile']
		parts = domain.replace('www.', '').split('.')
		print parts
		#jeśli użytkownik zdecydował, że nie chce wersji mobilnej
		if 'no_mobile' in request.session and request.session['no_mobile'] == True:
			"TUTUTUTUTUT 5"
			#adres mobilny wybrany bezpośrednio
			if parts[0] == 'm':
				request.META['HTTP_HOST'] = domain
				request.mobile = True
				request.urlconf = 'fereol.mobile_urls'#'fereol.mobile.urls'
			else:
				request.mobile = False
				request.urlconf = 'fereol.urls'

		elif parts[0] == 'm':
			request.mobile = True
			request.urlconf = 'fereol.mobile_urls'
			
		#wiadomość przekazana z MobileDetection
		elif request.is_mobile:
			request.META['HTTP_HOST'] = 'm.' + domain.replace('www.', '')
			request.mobile = True
			request.urlconf = 'fereol.mobile_urls'
			return HttpResponseRedirect(request.path)

		else:
			request.mobile = False
			request.urlconf = 'fereol.urls'
