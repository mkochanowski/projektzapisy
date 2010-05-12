from django.conf.urls.defaults import *


urlpatterns = patterns( 'fereol.offer.vote.views',
    url('^$', 'voteMain', name='vote-main' ),    
)

