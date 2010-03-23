from django.conf.urls.defaults import *

urlpatterns = patterns( 'fereol.subjects.views',
	( '^add/$', 'subjectForm' ),
	( '^edit/(?P<sid>[0-9]+)/$', 'subjectForm' ),
	
    ('(?P<slug>[\w\-_]+)', 'subject' ),
    ( '', 'subjects' ),
	
	
)

