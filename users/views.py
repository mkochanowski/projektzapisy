from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext

@login_required
def profile(request):
    return render_to_response('users/profile.html', context_instance = RequestContext( request ))

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')
