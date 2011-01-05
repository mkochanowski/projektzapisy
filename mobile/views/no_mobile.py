# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect

def noMobile(request):
	request.mobile = False
	request.session.set_expiry(0)
	request.session['no_mobile'] = True
	domain = request.META.get('HTTP_HOST', '')
	request.META['HTTP_HOST'] = domain.replace('www.', '').replace('m.', '')
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