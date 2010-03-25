from django.conf.urls.defaults import *

urlpatterns = patterns( 'fereol.records.views',
    ('(?P<group_id>[\d]+)', 'change' ),
    ( '', 'own' ),
)

