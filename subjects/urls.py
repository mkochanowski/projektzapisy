from django.conf.urls.defaults import *

urlpatterns = patterns( 'fereol.subjects.views',
    ( '^add/$', 'subjectForm' ),
    ( '^edit/(?P<sid>[0-9]+)/$', 'subjectForm' ),
    ( '^history/(?P<descid>[0-9]+)/$', 'subjectHistory' ),
    ( '^restore/(?P<descid>[0-9]+)/$', 'subjectRestore' ),
    ('(?P<slug>[\w\-_]+)', 'subject' ),
    ( '', 'subjects' ),
)
