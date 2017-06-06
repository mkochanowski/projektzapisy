from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.offer, name='offer-main'),
    url(r'^/teacher$', views.proposal, name='my-proposal'),
    url(r'^/teacher/(?P<slug>[\w\-_]+)$', views.proposal, name='my-proposal-show'),
    url('^/add$', views.proposal_edit, name='proposal-form' ),
    url('^/manage/proposals$', views.manage, name='manage' ),
    url('^/manage/select_for_voting$', views.select_for_voting),
    url('^/manage/groups$', views.all_groups),
    url('^/manage/groups/(?P<slug>[\w\-_]+)', views.course_groups),
    url('^/(?P<slug>[\w\-_]+)/accept', views.proposal_accept, name='proposal-accept'),
    url('^/(?P<slug>[\w\-_]+)/review', views.proposal_for_review, name='proposal-review'),
    url('^/(?P<slug>[\w\-_]+)/edit', views.proposal_edit, name='proposal-edit'),
    url('^/(?P<slug>[\w\-_]+)', views.offer, name='offer-page'),
]
