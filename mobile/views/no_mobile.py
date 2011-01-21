# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect

def noMobile(request):
	request.mobile = False
	request.session.set_expiry(0)
	request.session['no_mobile'] = True
	domain = request.META.get('HTTP_HOST', '')
	request.META['HTTP_HOST'] = domain.replace('www.', '').replace('m.', '')
	# TODO: wywalić urlconf, jeżeli się da (patrz: problemy np. z djdt).
	# więcej info, w razie potrzeby: Tomek Wasilczyk
	request.urlconf = 'fereol.urls'
	return HttpResponseRedirect('/')

def onMobile(request):
        request.mobile = True
	request.session.set_expiry(0)
	request.session['no_mobile'] = False
	domain = request.META.get('HTTP_HOST', '')
	request.META['HTTP_HOST'] = 'm.'+domain
	request.urlconf = 'fereol.mobile_urls'
	return HttpResponseRedirect('/')