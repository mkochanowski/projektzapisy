from django.conf.urls.defaults import *


urlpatterns = patterns( 'fereol.offer.vote.views',
    url('^$', 'voteMain',     name='vote-main' ),
    url('view/$', 'voteView', name='vote-view'),
    url('vote/$', 'vote',     name='vote')
)
