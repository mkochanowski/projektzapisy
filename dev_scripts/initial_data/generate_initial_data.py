#!/usr/bin/python
# -*- coding: utf8 -*-
# Author: Pawel Kacprzak

from random import randint as rand
from random import choice, seed, sample
import json
import sys

seed(0)

#########################################################################
#                        Setup & options                                #
#########################################################################

db_config_big = {
# students
	'NUM_OF_STUDENTS': 500,
	'ECTS_LOW': 0,
	'ECTS_HIGH': 300,
	'DELAY_MINUTES_FOR_STUDENT_LOW': 0,
	'DELAY_MINUTES_FOR_STUDENT_HIGH': 3 * 24 * 60,
	'STUDIES_PROGRAMS': [1, 2],
	'SEMESTERS_FOR_STUDIES_PROGRAMS': {1: [1, 2, 3, 4, 5, 6], 2: [1, 2, 3, 4]},
# employees
	'NUM_OF_EMPLOYEES': 50,
# classrooms
	'NUM_OF_CLASSROOMS': 30,
	'CLASSROOMS_NUMBERS': [i for i in range(1, 150)],
	'MIN_NON_LECTURE_GROUPS_FOR_COURSE': 1,
	'MAX_NON_LECTURE_GROUPS_FOR_COURSE': 5,
	'LECTURES_LIMITS': [20, 30, 40, 50, 60, 100, 200],
	'NON_LECTURE_LIMITS': [15, 20],
	'DELAY_MINUTES_FOR_COURSE_LOW': 0,
	'DELAY_MINUTES_FOR_COURSE_HIGH': 3 * 24 * 60,
	'NUM_OF_RECORDS': 3000,
	}

db_config_small = {
# students
	'NUM_OF_STUDENTS': 25,
	'ECTS_LOW': 0,
	'ECTS_HIGH': 300,
	'DELAY_MINUTES_FOR_STUDENT_LOW': 0,
	'DELAY_MINUTES_FOR_STUDENT_HIGH': 3 * 24 * 60,
	'STUDIES_PROGRAMS': [1, 2],
	'SEMESTERS_FOR_STUDIES_PROGRAMS': {1: [1, 2, 3, 4, 5, 6], 2: [1, 2, 3, 4]},
# employees
	'NUM_OF_EMPLOYEES': 10,
# classrooms
	'NUM_OF_CLASSROOMS': 10,
	'CLASSROOMS_NUMBERS': [i for i in range(1, 150)],
# groups
	'MIN_NON_LECTURE_GROUPS_FOR_COURSE': 1,
	'MAX_NON_LECTURE_GROUPS_FOR_COURSE': 5,
	'LECTURES_LIMITS': [20, 30, 40, 50, 60, 100, 200],
	'NON_LECTURE_LIMITS': [20, 30],
# students_options 
	'DELAY_MINUTES_FOR_COURSE_LOW': 0,
	'DELAY_MINUTES_FOR_COURSE_HIGH': 3 * 24 * 60,
# records
	'NUM_OF_RECORDS': 100,
	}
	

# SET BIG DATABASE CONFIG AS DEFAULT CONFIG
config = db_config_big

for arg in sys.argv[1:]:
	if arg == 'small':
		config = db_config_small
        print "change!"
	
COURSES = json.loads(open('courses_data.json', 'r').read())

# SETUP
file_input = 'static_data.json'
INDENT = 4

NAMES = json.loads(open('names_data.json', 'r').read())
MALE_FIRST_NAMES = NAMES['MALE_FIRST_NAMES']
FEMALE_FIRST_NAMES = NAMES['FEMALE_FIRST_NAMES']
MALE_LAST_NAMES = NAMES['MALE_LAST_NAMES']
FEMALE_LAST_NAMES = NAMES['FEMALE_LAST_NAMES']

#polls & sections
ADMIN_ID = 1 # id of admin user

#########################################################################
#                           Static data                                 #
#########################################################################

# BEGIN SCRIPT

spaces = ' ' * INDENT
s = u''

# Read static data and write it to begin of output
f_input = open(file_input, 'r')
input_data = f_input.read()
input_data = input_data[:-2] + ',\n'
s += input_data

#########################################################################
#               Generate users - students and employees                 #
#########################################################################

# Generate users
id_start = 200

# Generate users for student
username = 2
first_user_for_student_id = id_start
users_raw = []
for user_id in range(id_start, id_start + config['NUM_OF_STUDENTS']):
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

# Generate students
students_raw = []
for student_id in range(first_user_for_student_id, last_user_for_student_id + 1):
	ects = rand(config['ECTS_LOW'], config['ECTS_HIGH'])
	delay = rand(config['DELAY_MINUTES_FOR_STUDENT_LOW'], config['DELAY_MINUTES_FOR_STUDENT_HIGH'])
	program = choice(config['STUDIES_PROGRAMS'])
	semestr = choice(config['SEMESTERS_FOR_STUDIES_PROGRAMS'][program])
	record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "users.student",\n@!@@!@"fields": {\n@!@@!@@!@"ects": %s,\n@!@@!@@!@"records_opening_delay_minutes": %s,\n@!@@!@@!@"receive_mass_mail_offer": true,\n@!@@!@@!@"user": %s,\n@!@@!@@!@"matricula": "%s",\n@!@@!@@!@"program": %s,\n@!@@!@@!@"semestr": %s,\n@!@@!@@!@"receive_mass_mail_enrollment": true\n@!@@!@}\n@!@},\n' % (student_id, ects, delay, student_id, student_id, program, semestr)
	students_raw.append(record)
s += ''.join(students_raw)

# Generate users for employees
first_user_for_employee_id = id_start + config['NUM_OF_STUDENTS']
employees_raw = []
for user_id in range(id_start + config['NUM_OF_STUDENTS'], id_start + config['NUM_OF_STUDENTS'] + config['NUM_OF_EMPLOYEES']):
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

# Generate employees
employees_raw = []
list_employees = [1] + range(first_user_for_employee_id, last_user_for_employee_id + 1)
for employee_id in list_employees:
	record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "users.employee",\n@!@@!@"fields": {\n@!@@!@@!@"consultations": "pn 10:00 - 12:00",\n@!@@!@@!@"receive_mass_mail_offer": true,\n@!@@!@@!@"user": %s,\n@!@@!@@!@"receive_mass_mail_enrollment": true\n@!@@!@}\n@!@},\n' % (employee_id, employee_id)
	employees_raw.append(record)
s += ''.join(employees_raw)

#########################################################################
#                      Generate clasrooms                               #
#########################################################################

# Generate classrooms
classroom_id_start = 1
classrooms = []
classrooms_raw = []
for classroom_id in range(classroom_id_start, classroom_id_start + config['NUM_OF_CLASSROOMS']):
	number = choice(config['CLASSROOMS_NUMBERS'])
	while number in classrooms:
		number = choice(config['CLASSROOMS_NUMBERS'])
	record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "courses.classroom",\n@!@@!@"fields": {\n@!@@!@@!@"number": "%s"\n@!@@!@}\n@!@},\n' % (classroom_id, number)
	classrooms_raw.append(record)
classroom_id_end = classroom_id
s += ''.join(classrooms_raw)


#########################################################################
#                      Generate courses                                #
#########################################################################

# Generate courses
course_id_start = 1
course_id = course_id_start
courses_raw = []
semesters = [1,2,3,4]
courses = {}

# Generate courses in year 2009
for sub in COURSES:
    if sub['semester'] == 1:
        slug = '%s-zimowy-2009' % (sub['slug'])
        courses[course_id] = 1        
    else:
        slug = '%s-letni-2009' % (sub['slug'])
        courses[course_id] = 2
    record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "courses.course",\n@!@@!@"fields": {\n@!@@!@@!@"lectures": %s,\n@!@@!@@!@"name": "%s",\n@!@@!@@!@"entity": %s,\n@!@@!@@!@"semester": %s,\n@!@@!@@!@"exercises": %s,\n@!@@!@@!@"laboratories": %s,\n@!@@!@@!@"type": %s,\n@!@@!@@!@"slug": "%s",\n@!@@!@@!@"description": "Opis"\n@!@@!@}\n@!@},\n' % (course_id, sub['lectures'], sub['name'], sub['entity'], sub['semester'], sub['exercises'], sub['laboratories'], sub['type'], slug)
    courses_raw.append(record)
    course_id += 1
	
# Generate courses in year 2010
for sub in COURSES[:-2]:
    if sub['semester'] == 1:
        slug = '%s-zimowy-2010' % (sub['slug'])
        courses[course_id] = 3
    else:
        slug = '%s-letni-2010' % (sub['slug'])
        courses[course_id] = 4
    record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "courses.course",\n@!@@!@"fields": {\n@!@@!@@!@"lectures": %s,\n@!@@!@@!@"name": "%s",\n@!@@!@@!@"entity": %s,\n@!@@!@@!@"semester": %s,\n@!@@!@@!@"exercises": %s,\n@!@@!@@!@"laboratories": %s,\n@!@@!@@!@"type": %s,\n@!@@!@@!@"slug": "%s",\n@!@@!@@!@"description": "Opis"\n@!@@!@}\n@!@},\n' % (course_id, sub['lectures'], sub['name'], sub['entity'], sub['semester'] + 2, sub['exercises'], sub['laboratories'], sub['type'], slug)
    courses_raw.append(record)
    course_id += 1
	
course_id_end = course_id
s += ''.join(courses_raw)

#########################################################################
#                      Generate groups                                  #
#########################################################################

# Generate groups 
group_id_start = 1
group_id = group_id_start
groups_raw = []
groups_sem = {1: [], 2:[], 3: [], 4: []}

for course_id in range(course_id_start, course_id_end):

    teacher = rand(first_user_for_employee_id, last_user_for_employee_id)
    limit = choice(config['LECTURES_LIMITS'])
    record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "courses.group",\n@!@@!@"fields": {\n@!@@!@@!@"limit": %s,\n@!@@!@@!@"type": "1",\n@!@@!@@!@"teacher": %s,\n@!@@!@@!@"course": %s\n@!@@!@}\n@!@},\n' % (group_id, limit, teacher, course_id)
    groups_sem[ courses[course_id] ].append(group_id)
    groups_raw.append(record)
    group_id += 1
    groups = rand(config['MIN_NON_LECTURE_GROUPS_FOR_COURSE'], config['MAX_NON_LECTURE_GROUPS_FOR_COURSE'])	
    for i in range(1, groups + 1):
        teacher = rand(first_user_for_employee_id, last_user_for_employee_id)
        limit = choice(config['NON_LECTURE_LIMITS'])
        record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "courses.group",\n@!@@!@"fields": {\n@!@@!@@!@"limit": %s,\n@!@@!@@!@"type": "2",\n@!@@!@@!@"teacher": %s,\n@!@@!@@!@"course": %s\n@!@@!@}\n@!@},\n' % (group_id, limit, teacher, course_id)
        groups_sem[ courses[course_id] ].append(group_id)
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
	record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "courses.term",\n@!@@!@"fields": {\n@!@@!@@!@"dayOfWeek": "%s",\n@!@@!@@!@"classroom": %s,\n@!@@!@@!@"start_time": "%s:00:00",\n@!@@!@@!@"group": %s,\n@!@@!@@!@"end_time": "%s:00:00"\n@!@@!@}\n@!@},\n' % (term_id, day, classroom, start_hour, term_id, start_hour + 2)
	terms_raw.append(record)
s += ''.join(terms_raw)

# generate student_options

student_options_id = 1
student_options_raw = []
for student in range(first_user_for_student_id, last_user_for_student_id):
	for course in range(course_id_start, course_id_end):
		delay = rand(config['DELAY_MINUTES_FOR_COURSE_LOW'], config['DELAY_MINUTES_FOR_COURSE_HIGH'])
		record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "courses.studentoptions",\n@!@@!@"fields": {\n@!@@!@@!@"records_opening_delay_minutes": %s,\n@!@@!@@!@"student": %s,\n@!@@!@@!@"course": %s\n@!@@!@}\n@!@},\n' % (student_options_id, delay, student, course)
		student_options_raw.append(record)
		student_options_id += 1
s += ''.join(student_options_raw)

#########################################################################
#                      Generate records                                 #
#########################################################################

#generate_records

pairs = []

counter = 0
records_raw = []
for record_id in range(1, config['NUM_OF_RECORDS'] + 1):
	group = rand(group_id_start, group_id_end - 1)
	student = rand(first_user_for_student_id, last_user_for_student_id - 1)
	pair = (group, student)
	while pair in pairs:
		group = rand(group_id_start, group_id_end - 1)
		student = rand(first_user_for_student_id, last_user_for_student_id - 1)
		pair = (group, student)
		counter += 1
	counter = 0
	pairs.append(pair)
	record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "records.record",\n@!@@!@"fields": {\n@!@@!@@!@"status": "1",\n@!@@!@@!@"group": %s,\n@!@@!@@!@"student": %s\n@!@@!@}\n@!@},\n' % (record_id, group, student)
	records_raw.append(record)
s += ''.join(records_raw)
	
#########################################################################
#                      Generate polls                                   #
#########################################################################

poll_sections = {}

def generate_poll(poll_id, sec_total, sem, group, polls_raw):
    """
    Generate one poll for a specified group (or null)
    """
    if (group == "null"):
        n_sec = rand(1,3)
        sections = sample(range(1,4), n_sec)
    else:
        n_sec = rand(1,4)
        sections = sample(range(4,8), n_sec)
    poll_sections[poll_id] = sections
    poll = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "poll.poll",\n@!@@!@"fields": {\n@!@@!@@!@"studies_type": null,\n@!@@!@@!@"group": %s,\n@!@@!@@!@"description": "",\n@!@@!@@!@"title": "Ankieta",\n@!@@!@@!@"author": %s,\n@!@@!@@!@"semester": %s\n@!@@!@}\n@!@},\n' % (poll_id, group, ADMIN_ID, sem)
    polls_raw += poll
    sec_num = 1
    for sec_id in sections:
        section = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "poll.sectionordering",\n@!@@!@"fields": {\n@!@@!@@!@"position": %s,\n@!@@!@@!@"section": %s,\n@!@@!@@!@"poll": "%s"\n@!@@!@}\n@!@},\n' % (sec_total, sec_num, sec_id, poll_id)
        sec_total += 1
        polls_raw += section   
        sec_num += 1
    return (polls_raw, sec_total)
            
def generate_polls(semesters, groups):
    """
    Generates polls for all the groups created + one poll without group assigned per semester
    """
    polls_raw = []
    sec_total = 1
    poll_id = 1
    for sem in semesters:
        (polls_raw,sec_total) = generate_poll(poll_id, sec_total, sem, "null", polls_raw)
        poll_id += 1
        for group in groups[sem]:   
            (polls_raw,sec_total) = generate_poll(poll_id, sec_total, sem, group, polls_raw)
            poll_id += 1
    return polls_raw    
    
#s += ''.join( generate_polls(semesters, groups_sem) )

#########################################################################
#                      Generate answers for polls                       #
#########################################################################
ANSWERS = json.loads(open('answers_data.json', 'r').read())

def generate_answers(poll_id, amount, ans_id, ticket_id):
    answers_poll = ''
    for i in xrange(amount):
        ticket = '@!@{\n@!@@!@"pk": %s, "model": "poll.savedticket", "fields": {\n@!@@!@@!@"ticket": "0", "poll": %s, "finished": true\n@!@@!@}\n@!@},\n' % (ticket_id, poll_id)
        answers_poll += ticket
        for sec in poll_sections[poll_id]:
            ans_sec =  ANSWERS["SECTION"+str(sec)]
            for ans in ans_sec:
                if rand(1,10) > 3: # not all the questions will have answers 
                    if ans["model"] == "poll.singlechoicequestionanswer":
                        answer = choice(ans["answers"])
                        fields = '@!@@!@"question": %s, "section": %s, "saved_ticket": %s, "option": %s' % (ans["question"], sec, ticket_id, answer) 
                    elif ans["model"] == "poll.multiplechoicequestionanswer":
                        answer = sample(ans["answers"], rand(1,ans["limit"]))                        
                        fields = '@!@@!@"question": %s, "section": %s, "other": null, "saved_ticket": %s, "options": %s' % (ans["question"], sec, ticket_id, answer) 
                    elif ans["model"] == "poll.openquestionanswer":
                        answer = choice(ans["answers"])
                        fields = '@!@@!@"content": "%s", "question": %s, "section": %s, "saved_ticket": %s' % (answer, ans["question"], sec, ticket_id)                    
                    answers_poll += '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "%s",\n@!@@!@"fields": {\n@!@%s\n@!@@!@}\n@!@},\n' % (ans_id, ans["model"], fields)                    
                    ans_id += 1
        ticket_id += 1
    return (ans_id, ticket_id, answers_poll)
          
def generate_answers_full():
    answers_raw = []
    ans_id = 1
    ticket_id = 1
    for poll_id in iter(poll_sections):                
        (ans_id, ticket_id, answer) = generate_answers(poll_id, rand(5,15), ans_id, ticket_id)
        answers_raw += answer
    return answers_raw
    
#s += ''.join( generate_answers_full() )

# Convert to readable format using indents and add close bracket
s = s.replace('@!@', spaces)[:-2] + '\n]'
print s.encode('utf-8')
