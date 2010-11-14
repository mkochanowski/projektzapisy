# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect

def noMobile(request):
	request.mobile = False
	request.session.set_expiry(0)
	request.session['no_mobile'] = True
	domain = request.META.get('HTTP_HOST', '')
	request.META['HTTP_HOST'] = domain.replace('www.', '').replace('m.', '')
	return HttpResponseRedirect('/')
