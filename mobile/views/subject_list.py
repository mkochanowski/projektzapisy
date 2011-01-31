# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from fereol.enrollment.records.models import Record, STATUS_ENROLLED, STATUS_PINNED
from fereol.enrollment.subjects.models import Semester, Subject
from fereol.offer.vote.models import SingleVote
from users.models import Student

import logging
logger = logging.getLogger()

@login_required
def studentSubjectList(request):
	
	(subjects_enrolled, subjects_pinned, subjects_voted) = subjectsEnrolled(request)
	logger.info('User %s looked at his subject list' % (unicode(request.user.username)))
	return render_to_response("mobile/student_subjects.html", {'enrolled': subjects_enrolled, 'pinned': subjects_pinned, 'voted': subjects_voted}, context_instance = RequestContext(request))


@login_required
def otherSubjects(request):
	(subjects_enrolled, subjects_pinned, subjects_voted) = subjectsEnrolled(request)
	subjects_enrolled = [s['subject'] for s in subjects_enrolled]
	subj = subjects_enrolled + subjects_pinned + subjects_voted
	other_subjects = Subject.objects.all().order_by('name')
	other_subjects = filter(lambda s : s.semester.is_current_semester() and s not in subj, other_subjects)
	logger.info('User %s looked at other subject' % (unicode(request.user.username)))
	return render_to_response("mobile/other_subjects.html", {'subjects': other_subjects}, context_instance = RequestContext(request))



def subjectsEnrolled(request):
	try:
		student = request.user.student
	except Student.DoesNotExist:
		return ([], [], [])
	semester = Semester.objects.filter(visible = True)
	semester = filter(lambda s : s.is_current_semester(), semester) #???
	records = Record.objects.filter(student = student, group__subject__semester__in = semester).select_related('group', 'group__type', 'group__subject').order_by('group__subject').reverse()
	records_enr = filter(lambda r: r.status == STATUS_ENROLLED, records)
	groups_enrolled = [record.group for record in records_enr]
	subjects_enrolled_types = [{'subject': record.group.subject, 'types': [r.group.type for r in records if r.group.subject == record.group.subject]} for record in records_enr]


	_subjects_enrolled = []	
	for s in subjects_enrolled_types:
		groups = s['subject'].groups.all()
		types = [g.type for g in groups]
		allGroups = True
		for t in types:
			if t not in s['types']:
				allGroups = False
				break
		
		_subjects_enrolled.append({'subject':s['subject'], 'allGroups': allGroups})

	subjects_enrolled = _subjects_enrolled

	records_pin = filter(lambda r: r.status == STATUS_PINNED, records)
	subjects_pinned = [record.group.subject for record in records_pin]


	#votes = SingleVote.objects.filter(student = student, subject__semester__in = semester).select_related('subject')
	votes = SingleVote.objects.filter(student = student).select_related('subject').order_by('subject__name')
	proposals_voted = [v.subject.name for v in votes if v.state.year == semester[0].year]
	subjects_voted = Subject.objects.filter(name__in = proposals_voted).order_by('name').reverse()
	subjects_voted = filter(lambda s : s.semester.is_current_semester(), subjects_voted)
	#subjects_voted = [vote.subject for vote in votes]
	logger.info('User %s looked at his enrolled subject' % (unicode(request.user.username)))
	return (subjects_enrolled, subjects_pinned, subjects_voted)
