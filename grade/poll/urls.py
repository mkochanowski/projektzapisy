from django.conf.urls.defaults import *

urlpatterns = patterns('',

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
    url(r'managment/polls_list$', 'fereol.grade.poll.views.polls_list', name='grade-poll-list'),
    url(r'managment/sections_list$', 'fereol.grade.poll.views.sections_list', name='grade-poll-sections-list'),
    url(r'managment/groups_without_polls$', 'fereol.grade.poll.views.groups_without_poll', name='grade-poll-groups_without_polls'),
    url(r'managment/poll_create$', 'fereol.grade.poll.views.poll_create', name='grade-poll-poll-create'),
    url(r'managment/section_create$', 'fereol.grade.poll.views.questionset_create', name='grade-poll-questionset-create'),  
    url(r'managment/show_section/(?P<section_id>[1-9][0-9]*)/$', 'fereol.grade.poll.views.show_section', name='grade-poll-show_section'),
    url(r'managment/delete_sections$', 'fereol.grade.poll.views.delete_section', name='grade-poll-delete_section'),  
    url(r'managment/show_poll/(?P<poll_id>[1-9][0-9]*)/$', 'fereol.grade.poll.views.show_poll', name='grade-poll-show_poll'),
    url(r'managment/delete_polls$', 'fereol.grade.poll.views.delete_poll', name='grade-poll-delete_poll'),
           
    url(r'poll_manage$', 'fereol.grade.poll.views.poll_manage', name='grade-poll-poll-manage'),
    url(r'autocomplete$', 'fereol.grade.poll.views.autocomplete', name='grade-poll-autocomplete'),
    
    url(r'get_section/(?P<section_id>[1-9][0-9]*)/$', 'fereol.grade.poll.views.get_section', name='grade-poll-get-section'),
    url(r'edit_section/(?P<section_id>[1-9][0-9]*)/$', 'fereol.grade.poll.views.edit_section', name='grade-poll-edit-section'),
)
