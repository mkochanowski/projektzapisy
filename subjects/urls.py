from django.conf.urls.defaults import *

urlpatterns = patterns( 'fereol.subjects.views',
    ('(?P<slug>[\w\-_]+)', 'subject' ),
    ( '', 'subjects' ),
)

