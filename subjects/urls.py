from django.conf.urls.defaults import *

urlpatterns = patterns( 'fereol.subjects.views',
    ( '^add/$', 'subjectForm' ),
    ( '^edit/(?P<sid>[0-9]+)/$',        'subjectForm' ),
    ( '^history/(?P<sid>[0-9]+)/$',     'subjectHistory' ),
    ( '^archival/(?P<descid>[0-9]+)/$', 'subjectViewArcival' ),
    ( '^restore/(?P<descid>[0-9]+)/$',  'subjectRestore' ),
    url('^details/(?P<slug>[\w\-_]+)', 'subject', name='subject-page'),
    url('^$', 'subjects', name='subject-list' ),
)
