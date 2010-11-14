# -*- coding: utf-8 -*-
from fereol.enrollment.records.models import Record, STATUS_ENROLLED, STATUS_PINNED

def studentSubjectList(request):
	student = request.user.student
	records = Records.objects.filter(student = student, group__subject__semester__is_current = True).select_related('group', 'group__subject').order_by('group__subject')
	records_enr = filter(lambda r: r.status == STATUS_ENROLLED, records)
	subjects_enrolled = set([record.group.subject for record in records_enr ])
	
	records_pin = filter(lambda r: r.status == STATUS_PINNED, records)
	subjects_pinned = set([records.group.subject for record in records_pin])
	

def otherSubjects(request):
