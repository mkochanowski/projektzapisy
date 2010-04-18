from django.conf.urls.defaults import *

urlpatterns = patterns( 'fereol.offer.proposal.views',
    ( '^add/$', 'proposalForm' ),
    ( '^edit/(?P<sid>[0-9]+)/$',        'proposalForm' ),
    ( '^history/(?P<sid>[0-9]+)/$',     'proposalHistory' ),
    ( '^archival/(?P<descid>[0-9]+)/$', 'proposalViewArcival' ),
    ( '^restore/(?P<descid>[0-9]+)/$',  'proposalRestore' ),
    url('^details/(?P<slug>[\w\-_]+)', 'proposal', name='proposal-page'),
    url('^$', 'proposals', name='proposal-list' ),
)
