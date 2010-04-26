from django.conf.urls.defaults import *

urlpatterns = patterns( 'fereol.offer.proposal.views',
    ( '^add/$', 'proposalForm' ),
    url( '^edit/(?P<sid>[0-9]+)/$',                  'proposalForm',        name='proposal-edit' ),
    url( '^history/(?P<sid>[0-9]+)/$',               'proposalHistory',     name='proposal-history' ),
    url( '^archival/(?P<descid>[0-9]+)/$',           'proposalViewArcival', name='proposal-viewhistory' ),
    url( '^restore/(?P<descid>[0-9]+)/$',            'proposalRestore',     name='proposal-restore' ),
    url('^(?P<slug>[\w\-_]+)/(?P<descid>[0-9]+)/?$', 'proposal',            name='proposal-page-archival'),
    url('^(?P<slug>[\w\-_]+)',                       'proposal',            name='proposal-page'),
    #url('^details/(?P<slug>[\w\-_]+)',               'proposal',            name='proposal-page'),
    url('^$',                                        'proposals',           name='proposal-list' ),
)
