# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from apps.enrollment.records.models import Record, STATUS_ENROLLED
from apps.enrollment.courses.models import Semester, Course
from apps.offer.vote.models import SingleVote
from apps.users.models import Student

import logging
logger = logging.getLogger()

@login_required
def studentCourseList(request):
	"""
		A function returning lists of courses the authenticated user has been enrolled to or has voted for.
	"""
	(courses_enrolled, courses_voted) = coursesEnrolled(request)
	logger.info('User %s looked at his course list' % (unicode(request.user.username)))
	return render_to_response("mobile/student_courses.html", {'enrolled': courses_enrolled, 'voted': courses_voted}, context_instance = RequestContext(request))


@login_required
def otherCourses(request):
	"""
		A function returning the list of all courses from the current semester.
		After adding the
			and s not in subj
		fragment of code, it returns the list of current semester courses not returned by studentCourseList.
	"""
	(courses_enrolled, courses_voted) = coursesEnrolled(request)
	courses_enrolled = [s['course'] for s in courses_enrolled]
	subj = courses_enrolled + courses_voted
	other_courses = Course.objects.all().order_by('name')
	other_courses = filter(lambda s : s.semester.is_current_semester(), other_courses) # and s not in subj #dla listy innych, nie wszystkich
	logger.info('User %s looked at other course' % (unicode(request.user.username)))

	return render_to_response("mobile/other_subjects.html", {'courses': other_courses}, context_instance = RequestContext(request))



def coursesEnrolled(request):
	try:
		student = request.user.student
	except Student.DoesNotExist:
		return ([], [], [])
	semester = Semester.objects.filter(visible = True)
	semester = filter(lambda s : s.is_current_semester(), semester) #???
	records = Record.objects.filter(student = student, group__course__semester__in = semester).select_related('group', 'group__type', 'group__course').order_by('group__course').reverse()
	records_enr = filter(lambda r: r.status == STATUS_ENROLLED, records)
	groups_enrolled = [record.group for record in records_enr]
	courses_enrolled_types = [{'course': record.group.course, 'types': [r.group.type for r in records if r.group.course == record.group.course]} for record in records_enr]


	_courses_enrolled = []
	done = []
	for s in courses_enrolled_types:
		groups = s['course'].groups.all()
		types = [g.type for g in groups]
		allGroups = True
		for t in types:
			if t not in s['types']:
				allGroups = False
				break
		
		if s['course'] not in done:
			_courses_enrolled.append({'course':s['course'], 'allGroups': allGroups})
		done.append(s['course'])

	courses_enrolled = _courses_enrolled

	#votes = SingleVote.objects.filter(student = student, course__semester__in = semester).select_related('course')
	#votes = SingleVote.objects.filter(student = student).select_related('course').order_by('course__name')
	votes = SingleVote.get_votes(student)
	proposals_voted = [v.course.name for v in votes] #if v.state.year == semester[0].year]
	courses_voted = Course.objects.filter(name__in = proposals_voted).order_by('name')
	courses_voted = filter(lambda s : s.semester.is_current_semester(), courses_voted)
	#courses_voted = [vote.course for vote in votes]
	logger.info('User %s looked at his enrolled course' % (unicode(request.user.username)))
	return (courses_enrolled, courses_voted)
