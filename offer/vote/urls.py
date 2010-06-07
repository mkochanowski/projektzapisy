from django.conf.urls.defaults import *


urlpatterns = patterns( 'fereol.offer.vote.views',
    url('^$',     'vote_main', name='vote-main' ),
    url('view/$', 'vote_view', name='vote-view'),
    url('vote/$', 'vote',      name='vote')
)
