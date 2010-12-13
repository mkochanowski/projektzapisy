from django.conf.urls.defaults import *

# to tree/list_view and description, pass by GET:
# format=json - returns data as json
# format=html - returns data rendered with template, not using the base template
# by default, they return a fully rendered page

urlpatterns = patterns('',
    url(r'^$',                      'fereol.grade.poll.views.default',                           name='grade-default'),
    url(r'create$',                 'fereol.grade.poll.views.create',                            name='grade-poll-add'),
    url(r'^check_keys$',            'fereol.grade.poll.views.check_keys',                        name='grade-poll-verify-keys'),
    url(r'^enable_grade$',          'fereol.grade.cryptography.views.enable_grade',              name='grade-cryptography-start-grading'),
    url(r'^disable_grade$',         'fereol.grade.cryptography.views.disable_grade',             name='grade-cryptography-stop-grading'),
    url(r'^get_tickets_for_grade$', 'fereol.grade.signature_server.views.get_tickets_for_grade', name='grade-signature_server-sign-tickets'),
    url(r'^generate_tickets_sign$', 'fereol.grade.signature_server.views.generate_tickets_sign', name='grade-signature_server-generate-tickets'),
)
