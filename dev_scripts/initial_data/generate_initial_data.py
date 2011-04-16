#!/usr/bin/python
# -*- coding: utf8 -*-
# Author: Pawel Kacprzak

from random import randint as rand
from random import choice, seed
import json
import sys

seed(0)

opt_bigdb = True
for arg in sys.argv[1:]:
	if arg == 'small':
		opt_bigdb = False

SUBJECTS = json.loads(open('subjects_data.json', 'r').read())

# SETUP
file_input = 'static_data.json'

# students
NUM_OF_STUDENTS = 500 if opt_bigdb else 25
ECTS_LOW = 0
ECTS_HIGH = 300
DELAY_MINUTES_FOR_STUDENT_LOW = 0
DELAY_MINUTES_FOR_STUDENT_HIGH = 3 * 24 * 60
STUDIES_PROGRAMS = [1, 2] 

# employees
NUM_OF_EMPLOYEES = 50 if opt_bigdb else 10

#classrooms
NUM_OF_CLASSROOMS = 30 if opt_bigdb else 10
CLASSROOMS_NUMBERS = [i for i in range(1, 150)]

#groups
MIN_NON_LECTURE_GROUPS_FOR_SUBJECT = 1
MAX_NON_LECTURE_GROUPS_FOR_SUBJECT = 5
LECTURES_LIMITS = [20, 30, 40, 50, 60, 100, 200]
NON_LECTURE_LIMITS = [20, 30]

#students_options 
DELAY_MINUTES_FOR_SUBJECT_LOW = 0
DELAY_MINUTES_FOR_SUBJECT_HIGH = 3 * 24 * 60
#records
NUM_OF_RECORDS = 3000 if opt_bigdb else 100

INDENT = 4

NAMES = json.loads(open('names_data.json', 'r').read())
MALE_FIRST_NAMES = NAMES['MALE_FIRST_NAMES']
FEMALE_FIRST_NAMES = NAMES['FEMALE_FIRST_NAMES']
MALE_LAST_NAMES = NAMES['MALE_LAST_NAMES']
FEMALE_LAST_NAMES = NAMES['FEMALE_LAST_NAMES']

# BEGIN SCRIPT

spaces = ' ' * INDENT
s = u''

# Read static data and write it to begin of output
f_input = open(file_input, 'r')
input_data = f_input.read()
input_data = input_data[:-2] + ',\n'
s += input_data
# Generate users
id_start = 2

# Generate users for student
username = 2
first_user_for_student_id = id_start
users_raw = []
for user_id in range(id_start, id_start + NUM_OF_STUDENTS):
	if user_id % 2:
		first_name = choice(MALE_FIRST_NAMES)
		last_name = choice(MALE_LAST_NAMES)
	else:
		first_name = choice(FEMALE_FIRST_NAMES)
		last_name = choice(FEMALE_LAST_NAMES)
	record = u'@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "auth.user",\n@!@@!@"fields": {\n@!@@!@@!@"username": "%s",\n@!@@!@@!@"first_name": "%s",\n@!@@!@@!@"last_name": "%s",\n@!@@!@@!@"is_active": true,\n@!@@!@@!@"is_superuser": false,\n@!@@!@@!@"is_staff": false,\n@!@@!@@!@"last_login": "2010-11-04 14:43:11",\n@!@@!@@!@"groups": [],\n@!@@!@@!@"user_permissions": [],\n@!@@!@@!@"password": "sha1$9915f$38f8781f7fbaed11078a9f38295b7bea1f871cb7",\n@!@@!@@!@"email": "%s.%s@fereol.pl",\n@!@@!@@!@"date_joined": "2010-11-04 14:42:09"\n@!@@!@}\n@!@},\n' % (user_id, username, first_name, last_name, first_name.lower(), last_name.lower())
	record = record.replace('@!@', spaces)
	users_raw.append(record)
	username += 1
last_user_for_student_id = user_id
s += ''.join(users_raw)

# Generate users for employees
first_user_for_employee_id = id_start + NUM_OF_STUDENTS
employees_raw = []
for user_id in range(id_start + NUM_OF_STUDENTS, id_start + NUM_OF_STUDENTS + NUM_OF_EMPLOYEES):
	if user_id % 2:
		first_name = choice(MALE_FIRST_NAMES)
		last_name = choice(MALE_LAST_NAMES)
	else:
		first_name = choice(FEMALE_FIRST_NAMES)
		last_name = choice(FEMALE_LAST_NAMES)
	record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "auth.user",\n@!@@!@"fields": {\n@!@@!@@!@"username": "%s",\n@!@@!@@!@"first_name": "%s",\n@!@@!@@!@"last_name": "%s",\n@!@@!@@!@"is_active": true,\n@!@@!@@!@"is_superuser": false,\n@!@@!@@!@"is_staff": false,\n@!@@!@@!@"last_login": "2010-11-04 14:43:11",\n@!@@!@@!@"groups": [],\n@!@@!@@!@"user_permissions": [],\n@!@@!@@!@"password": "sha1$9915f$38f8781f7fbaed11078a9f38295b7bea1f871cb7",\n@!@@!@@!@"email": "%s.%s@fereol.pl",\n@!@@!@@!@"date_joined": "2010-11-04 14:42:09"\n@!@@!@}\n@!@},\n' % (user_id, username, first_name, last_name, first_name.lower(), last_name.lower())
	employees_raw.append(record)
	username += 1
last_user_for_employee_id = user_id
s += ''.join(employees_raw)

# Generate classrooms
classroom_id_start = 1
classrooms = []
classrooms_raw = []
for classroom_id in range(classroom_id_start, classroom_id_start + NUM_OF_CLASSROOMS):
	number = choice(CLASSROOMS_NUMBERS)
	while number in classrooms:
		number = choice(CLASSROOMS_NUMBERS)
	record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "subjects.classroom",\n@!@@!@"fields": {\n@!@@!@@!@"number": "%s"\n@!@@!@}\n@!@},\n' % (classroom_id, number)
	classrooms_raw.append(record)
classroom_id_end = classroom_id
# Generate students
s += ''.join(classrooms_raw)

students_raw = []
for student_id in range(first_user_for_student_id, last_user_for_student_id + 1):
	ects = rand(ECTS_LOW, ECTS_HIGH)
	delay = rand(DELAY_MINUTES_FOR_STUDENT_LOW, DELAY_MINUTES_FOR_STUDENT_HIGH)
	program = choice(STUDIES_PROGRAMS)
	record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "users.student",\n@!@@!@"fields": {\n@!@@!@@!@"ects": %s,\n@!@@!@@!@"records_opening_delay_minutes": %s,\n@!@@!@@!@"receive_mass_mail_offer": true,\n@!@@!@@!@"user": %s,\n@!@@!@@!@"matricula": "%s",\n@!@@!@@!@"program": %s,\n@!@@!@@!@"receive_mass_mail_enrollment": true\n@!@@!@}\n@!@},\n' % (student_id, ects, delay, student_id, student_id, program)
	students_raw.append(record)
s += ''.join(students_raw)
	
# Generate employees

employees_raw = []
for employee_id in range(first_user_for_employee_id, last_user_for_employee_id + 1):
	ects = rand(ECTS_LOW, ECTS_HIGH)
	delay = rand(DELAY_MINUTES_FOR_STUDENT_LOW, DELAY_MINUTES_FOR_STUDENT_HIGH)
	program = choice(STUDIES_PROGRAMS)
	record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "users.employee",\n@!@@!@"fields": {\n@!@@!@@!@"consultations": "pn 10:00 - 12:00",\n@!@@!@@!@"receive_mass_mail_offer": true,\n@!@@!@@!@"user": %s,\n@!@@!@@!@"receive_mass_mail_enrollment": true\n@!@@!@}\n@!@},\n' % (employee_id, employee_id)
	employees_raw.append(record)
s += ''.join(employees_raw)

# Generate subjects

subject_id_start = 1
subject_id = subject_id_start
subjects_raw = []
# Generate subjects in year 2009
for sub in SUBJECTS:
	if sub['semester'] == 1:
		slug = '%s-zimowy-2009' % (sub['slug'])
	else:
		slug = '%s-letni-2009' % (sub['slug'])
	record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "subjects.subject",\n@!@@!@"fields": {\n@!@@!@@!@"lectures": %s,\n@!@@!@@!@"name": "%s",\n@!@@!@@!@"entity": %s,\n@!@@!@@!@"semester": %s,\n@!@@!@@!@"exercises": %s,\n@!@@!@@!@"laboratories": %s,\n@!@@!@@!@"type": %s,\n@!@@!@@!@"slug": "%s",\n@!@@!@@!@"description": "Opis"\n@!@@!@}\n@!@},\n' % (subject_id, sub['lectures'], sub['name'], sub['entity'], sub['semester'], sub['exercises'], sub['laboratories'], sub['type'], slug)
	subjects_raw.append(record)
	subject_id += 1
	
# Generate subjects in year 2010
for sub in SUBJECTS[:-2]:
	if sub['semester'] == 1:
		slug = '%s-zimowy-2010' % (sub['slug'])
	else:
		slug = '%s-letni-2010' % (sub['slug'])
	record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "subjects.subject",\n@!@@!@"fields": {\n@!@@!@@!@"lectures": %s,\n@!@@!@@!@"name": "%s",\n@!@@!@@!@"entity": %s,\n@!@@!@@!@"semester": %s,\n@!@@!@@!@"exercises": %s,\n@!@@!@@!@"laboratories": %s,\n@!@@!@@!@"type": %s,\n@!@@!@@!@"slug": "%s",\n@!@@!@@!@"description": "Opis"\n@!@@!@}\n@!@},\n' % (subject_id, sub['lectures'], sub['name'], sub['entity'], sub['semester'] + 2, sub['exercises'], sub['laboratories'], sub['type'], slug)
	subjects_raw.append(record)
	subject_id += 1
	
subject_id_end = subject_id
s += ''.join(subjects_raw)

# Generate groups 
group_id_start = 1
group_id = group_id_start
groups_raw = []
for subject_id in range(subject_id_start, subject_id_end):
	teacher = rand(first_user_for_employee_id, last_user_for_employee_id)
	limit = choice(LECTURES_LIMITS)
	record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "subjects.group",\n@!@@!@"fields": {\n@!@@!@@!@"limit": %s,\n@!@@!@@!@"type": "1",\n@!@@!@@!@"teacher": %s,\n@!@@!@@!@"subject": %s\n@!@@!@}\n@!@},\n' % (group_id, limit, teacher, subject_id)
	groups_raw.append(record)
	group_id += 1
	groups = rand(MIN_NON_LECTURE_GROUPS_FOR_SUBJECT, MAX_NON_LECTURE_GROUPS_FOR_SUBJECT)	
	for i in range(1, groups + 1):
		teacher = rand(first_user_for_employee_id, last_user_for_employee_id)
		limit = choice(NON_LECTURE_LIMITS)
		record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "subjects.group",\n@!@@!@"fields": {\n@!@@!@@!@"limit": %s,\n@!@@!@@!@"type": "2",\n@!@@!@@!@"teacher": %s,\n@!@@!@@!@"subject": %s\n@!@@!@}\n@!@},\n' % (group_id, limit, teacher, subject_id)
		groups_raw.append(record)
		group_id += 1
		
group_id_end = group_id
s += ''.join(groups_raw)

# Generate terms

triples = []

terms_raw = []
for term_id in range(group_id_start, group_id_end):
	day = rand(1, 5)
	classroom = rand(classroom_id_start, classroom_id_end)
	start_hour = 2 * rand(4, 9)
	triple = (day, classroom, start_hour)
	
	while triple in triples:
		day = rand(1, 5)
		classroom = rand(classroom_id_start, classroom_id_end)
		start_hour = 2 * rand(4, 9)
		triple = (day, classroom, start_hour)
	triples.append(triple)
	record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "subjects.term",\n@!@@!@"fields": {\n@!@@!@@!@"dayOfWeek": "%s",\n@!@@!@@!@"classroom": %s,\n@!@@!@@!@"start_time": "%s:00:00",\n@!@@!@@!@"group": %s,\n@!@@!@@!@"end_time": "%s:00:00"\n@!@@!@}\n@!@},\n' % (term_id, day, classroom, start_hour, term_id, start_hour + 2)
	terms_raw.append(record)
s += ''.join(terms_raw)

# generate student_options

student_options_id = 1
student_options_raw = []
for student in range(first_user_for_student_id, last_user_for_student_id):
	for subject in range(subject_id_start, subject_id_end):
		delay = rand(DELAY_MINUTES_FOR_SUBJECT_LOW, DELAY_MINUTES_FOR_SUBJECT_HIGH)
		record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "subjects.studentoptions",\n@!@@!@"fields": {\n@!@@!@@!@"records_opening_delay_minutes": %s,\n@!@@!@@!@"student": %s,\n@!@@!@@!@"subject": %s\n@!@@!@}\n@!@},\n' % (student_options_id, delay, student, subject)
		student_options_raw.append(record)
		student_options_id += 1
s += ''.join(student_options_raw)

#generate_records

pairs = []

counter = 0
records_raw = []
for record_id in range(1, NUM_OF_RECORDS + 1):
	group = rand(group_id_start, group_id_end - 1)
	student = rand(first_user_for_student_id, last_user_for_student_id - 1)
	pair = (group, student)
	while pair in pairs:
		group = rand(group_id_start, group_id_end - 1)
		student = rand(first_user_for_student_id, last_user_for_student_id - 1)
		pair = (group, student)
		counter += 1
#		print counter
#		print "losuje: g=%s, s=%s" % (group, student)
	counter = 0
	pairs.append(pair)
	record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "records.record",\n@!@@!@"fields": {\n@!@@!@@!@"status": "1",\n@!@@!@@!@"group": %s,\n@!@@!@@!@"student": %s\n@!@@!@}\n@!@},\n' % (record_id, group, student)
	records_raw.append(record)
s += ''.join(records_raw)
	
# Convert to readable format using indents and add close bracket
s = s.replace('@!@', spaces)[:-2] + '\n]'

print s.encode('utf-8')
