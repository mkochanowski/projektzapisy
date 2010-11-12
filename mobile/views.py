# Create your views here.
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext

def noMobile(request):
	request.mobile = False
	request.session.set_expiry(0)
	request.session['no_mobile'] = True
	domain = request.META.get('HTTP_HOST', '')
	request.META['HTTP_HOST'] = domain.replace('www.', '').replace('m.', '')
	return HttpResponseRedirect('/')

def main_page( request ):
    """
        Main page
    """
    return render_to_response('mobile/index_m.html', context_instance = RequestContext(request))
