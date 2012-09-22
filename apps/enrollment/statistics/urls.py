from django.conf.urls import patterns, url

urlpatterns = patterns( 'apps.enrollment.statistics.views',
    url('^$',     'students_list', name='statistics-main' ),
)
