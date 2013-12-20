from django.conf.urls import patterns, url

urlpatterns = patterns( 'apps.statistics.views',
    url('^$',     'main', name='main' ),
    url('^students/$',     'students', name='students' ),
    url('^groups/$',     'groups', name='groups' ),
    url('^vote/$',     'votes', name='vote' ),
    url('^swap/$',         'swap', name='swap')
)
