from django.conf.urls.defaults import *

urlpatterns = patterns( 'apps.offer.proposal.views',
    url(r'^$', 'offer', name='offer-main'),
    url(r'^/my$', 'proposal', name='my-proposal'),
    url( '^/add$', 'proposal_edit', name='proposal-form' ),
    url('^/(?P<slug>[\w\-_]+)/edit',                       'proposal_edit',                    name='proposal-edit'),
    url('^/(?P<slug>[\w\-_]+)',                       'offer',                    name='offer-page'),


)
"""
+ 1. widok oferty
+ 2. widok propozycji w ofercie
3. widok 'moich'
4. widok propozycji w 'moich'
5. formularz edycji
"""