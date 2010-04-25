# -*- coding: utf-8 -*-

from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse

from exceptions import NonUserException
from forms import EmailChangeForm


def profile(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        return render_to_response('users/profile.html', {'profile' : user})
    except NonUserException:
        pass
    #dodac redirecta

@login_required
# to ma dostac inna nazwe, poniewaz pod "profile" zrobilem profil uzytkownika o podanym id, 
# ktory nie jest koniecznie planem zajec np. profil wykladowcy       - P.Kacprzak

#def profile(request):
#   return redirect('/records/schedule', context_instance = RequestContext( request ))

def email_change(request):
    if request.POST:
        data = request.POST.copy()
        form = EmailChangeForm(data, instance=request.user)
        if form.is_valid():
            form.save()
            request.user.message_set.create(message="Twój adres e-mail został zmieniony.")
            return HttpResponseRedirect(reverse('my-profile'))
    else:
        form = EmailChangeForm({'email' : request.user.email})
    return render_to_response('users/email_change_form.html', {'form' : form}, context_instance = RequestContext( request ))

@login_required  
def password_change_done(request):
     request.user.message_set.create(message="Twóje hasło zostało zmienione.")
     return HttpResponseRedirect(reverse('my-profile'))
 
@login_required  
def my_profile(request):
    return render_to_response('users/my_profile.html', context_instance = RequestContext( request ))

@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')
