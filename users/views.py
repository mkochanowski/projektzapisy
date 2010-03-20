from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect

@login_required
def profile(request):
    data = {
        'user': request.user,
    }
    return render_to_response('users/profile.html', data)

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')