from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

@login_required
def logout(request):
    '''logout'''
    logger.info('User (%s) is logged off ' % request.user.get_full_name())
    auth.logout(request)
    return HttpResponseRedirect('/')
