from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'poll_create$', 'fereol.grade.poll.views.poll_create', name='grade-poll-poll-create'),
    url(r'questionset_create$', 'fereol.grade.poll.views.questionset_create', name='grade-poll-questionset-create'),
    url(r'questionset_assign$', 'fereol.grade.poll.views.questionset_assign', name='grade-poll-questionset-assign'),
    url(r'ajax_get_subjects$',  'fereol.grade.poll.views.ajax_get_subjects',  name='grade-poll-get-subjects'),
    url(r'ajax_get_groups$',    'fereol.grade.poll.views.ajax_get_groups',    name='grade-poll-get-groups'),

    url(r'tickets_enter$', 'fereol.grade.poll.views.tickets_enter', name='grade-poll-tickets-enter'),
    url(r'poll_answer$', 'fereol.grade.poll.views.poll_answer', name='grade-poll-questionset-poll-answer'),
    url(r'poll_save$', 'fereol.grade.poll.views.poll_save', name='grade-poll-poll-save'),
    
    url(r'poll_results$', 'fereol.grade.poll.views.poll_results', name='grade-poll-poll-results'),
)
