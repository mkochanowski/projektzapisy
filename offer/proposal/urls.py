from django.conf.urls.defaults import *

urlpatterns = patterns( 'fereol.offer.proposal.views',
    ( '^add/$', 'proposal_form' ),
    url('^offer/create/$',                           'offerCreate',            name='proposal-offer-create'),
    url('^offer/select/$',                           'offerSelect',            name='proposal-offer-select'),
    url( '^becomeFan/(?P<slug>[\w\-_]+)/$',          'become_fan',             name='proposal-beFan' ),
    url( '^becomeTeacher/(?P<slug>[\w\-_]+)/$',      'become_teacher',         name='proposal-beTeacher' ),
    url( '^stopBeFan/(?P<slug>[\w\-_]+)/$',          'stop_be_fan',            name='proposal-StopFan' ),
    url( '^stopBeTeacher/(?P<slug>[\w\-_]+)/$',      'stop_be_teacher',        name='proposal-StopTeacher' ),
    url( '^edit/(?P<sid>[0-9]+)/$',                  'proposal_form',          name='proposal-edit' ),
    url( '^history/(?P<sid>[0-9]+)/$',               'proposal_history',       name='proposal-history' ),
    url( '^restore/(?P<descid>[0-9]+)/$',            'proposal_restore',       name='proposal-restore' ),
    url('^(?P<slug>[\w\-_]+)/(?P<descid>[0-9]+)/?$', 'proposal',               name='proposal-page-archival'),
    url('^(?P<slug>[\w\-_]+)',                       'proposal',               name='proposal-page'),
    url('^$',                                        'proposals',              name='proposal-list' ),    
)
