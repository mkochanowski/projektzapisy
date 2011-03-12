# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
import logging
logger = logging.getLogger()


def noMobile(request):
    """
        Stores information in the session about user's choice to use the full version.
    """
    request.mobile = False
    request.session.set_expiry(0)
    request.session['no_mobile'] = True
    domain = request.META.get('HTTP_HOST', '')
    request.META['HTTP_HOST'] = domain.replace('www.', '').replace('m.', '')
    # TODO: wywalić urlconf, jeżeli się da (patrz: problemy np. z djdt).
    # więcej info, w razie potrzeby: Tomek Wasilczyk
    request.urlconf = 'fereol.urls'
    logger.info('User %s switch to fereol' % (request.user)) 
    return HttpResponseRedirect('/')

def onMobile(request):
    """
        Stores information in the session about user's choice to use the mobile version.
    """
    request.mobile = True
    request.session.set_expiry(0)
    request.session['no_mobile'] = False
    domain = request.META.get('HTTP_HOST', '')
    request.META['HTTP_HOST'] = 'm.'+domain
    request.urlconf = 'fereol.mobile_urls'
    logger.info('User %s switch to mobile fereol' % (request.user))
    return HttpResponseRedirect('/')
