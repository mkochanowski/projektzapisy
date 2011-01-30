from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'poll_create$', 'fereol.grade.poll.views.poll_create', name='grade-poll-poll-create'),
    url(r'questionset_create$', 'fereol.grade.poll.views.questionset_create', name='grade-poll-questionset-create'),
    url(r'questionset_assign$', 'fereol.grade.poll.views.questionset_assign', name='grade-poll-questionset-assign'),
    url(r'ajax_get_subjects$',  'fereol.grade.poll.views.ajax_get_subjects',  name='grade-poll-get-subjects'),
    url(r'ajax_get_groups$',    'fereol.grade.poll.views.ajax_get_groups',    name='grade-poll-get-groups'),

    url(r'tickets_enter$', 'fereol.grade.poll.views.tickets_enter', name='grade-poll-tickets-enter'),
    
    #- url(r'polls/$',         'fereol.grade.poll.views.polls_for_user', name='grade-poll-polls-for-user'),
    url(r'polls/(?P<slug>[\w\-_]+)$',         'fereol.grade.poll.views.polls_for_user', name='grade-poll-polls-for-user'),
    
    url(r'poll_answer/(?P<slug>[\w\-_]+)/(?P<pid>[0-9]+)/$', 'fereol.grade.poll.views.poll_answer', name='grade-poll-poll-answer'),
    url(r'end_grading/$', 'fereol.grade.poll.views.poll_end_grading', name='poll-end-grading'),
    #- url(r'poll_save$', 'fereol.grade.poll.views.poll_save', name='grade-poll-poll-save'),
    
    url(r'poll_results$', 'fereol.grade.poll.views.poll_results', name='grade-poll-poll-results'),
    url(r'poll_manage$', 'fereol.grade.poll.views.poll_manage', name='grade-poll-poll-manage'),
    url(r'autocomplete$', 'fereol.grade.poll.views.autocomplete', name='grade-poll-autocomplete'),
)
