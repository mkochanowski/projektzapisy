#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import re
import os.path
from os import mkdir
from sys import stdout
import time
import datetime

if not os.path.exists('cache'):
	mkdir('cache')

def get_cached_url(stype, sid):
	url = None
	if stype == 'list':
		url = 'http://iiuwr.indefero.net/p/fereol/issues/?_px_sk=modif_dtime&_px_so=a&_px_p=' + str(sid)
	if stype == 'issue':
		url = 'http://iiuwr.indefero.net/p/fereol/issues/' + str(sid) + '/'

	cache_file_name = 'cache/' + stype + '-' + str(sid)
	if os.path.exists(cache_file_name):
		f = open(cache_file_name, 'r')
		contents = f.read()
		f.close()
		return contents
	
	stdout.write('pobieram [' + stype + '/' + str(sid) + ']... ')
	f = urllib.urlopen(url)
	contents = f.read()
	f.close()
	print 'OK'
	
	f = open(cache_file_name, 'w')
	f.write(contents)
	f.close()
	
	return contents

def get_list(page):
	contents = get_cached_url('list', page)
	
	m = re.search('class="recent-issues">(.*)</table>', contents, re.DOTALL)
	contents = m.group(0)
	m = re.search('<tbody>(.*)</tbody>', contents, re.DOTALL)
	contents = m.group(0)
	
	raw_list = re.findall('<tr>(.*?)</tr>', contents, re.DOTALL)
	
	id_list = []
	
	for row in raw_list:
		id_cell = re.findall('<td.*?>.*?</td>', row, re.DOTALL)[0]
		sid = re.search('>(.*)<', id_cell, re.DOTALL)
		id_list.append(int(sid.group(1)))
	
	return id_list

def get_pages_no():
	contents = get_cached_url('list', 1)
	
	m = re.search('<tfoot>(.*)</tfoot>', contents, re.DOTALL)
	contents = m.group(1)
	pages = re.findall('<a.*?>([0-9]+)</a>', contents, re.DOTALL)
	
	return max(map(lambda strp: int(strp), pages))

class IssueInfo:
	class StatusType:
		NEW = 0
		ACCEPTED = 1
		STARTED = 2
		FIXED = 3
	class PriorityType:
		LOW = 0
		MEDIUM = 1
		HIGH = 2
		CRITICAL = 3
	class IssueTypeType:
		DEFECT = 0
		ENHANCEMENT = 1
		TASK = 2
		COSMETIC = 3
	iid = None
	status = None
	title = None
	owner = None
	priority = None
	issueType = None
	contents = None
	categoryID = None
	issueDate = None
	author = None
	
	def __init__(self, iid):
		self.iid = iid
	
	def setStatus(self, txt):
		if txt == 'New':
			self.status = self.StatusType.NEW
		elif txt == 'Accepted':
			self.status = self.StatusType.ACCEPTED
		elif txt == 'Started':
			self.status = self.StatusType.STARTED
		elif txt == 'Fixed':
			raise RuntimeError('Nie powinno być')
			self.status = self.StatusType.FIXED
		else:
			raise RuntimeError('Nieznany status: ' + txt)
	
	def setTitle(self, txt):
		m = re.search('^\\[(.+?)\\](.+?)$', txt)
		self.setTag(str(m.group(1)))
		self.title = m.group(2).strip('- ').capitalize()
	
	def setTag(self, txt):
		txt = txt.lower()
		if txt == 'Z':
			self.categoryID = 4
		elif txt == 'ocena':
			self.categoryID = 6
		elif txt == 'ocena uwagi':
			self.categoryID = 6
			self.issueType = self.IssueTypeType.COSMETIC
		elif txt == 'ocena test failure':
			self.categoryID = 6
			self.contents = '[ocena test failure]\n\n' + self.contents
		elif txt == 'sz2' or txt == 'zs2' or txt == 'sz' or txt == 'z':
			self.categoryID = 4
		elif txt == 'od':
			self.categoryID = 5
		elif txt == 'all':
			self.categoryID = 15
		elif txt == 'od,sz2':
			self.categoryID = 1
		else:
			raise RuntimeError('Nieznany tag: ' + txt)
	
	def setPriority(self, txt):
		if txt == 'Low':
			self.priority = self.PriorityType.LOW
		elif txt == 'Medium':
			self.priority = self.PriorityType.MEDIUM
		elif txt == 'High':
			self.priority = self.PriorityType.HIGH
		elif txt == 'Critical':
			self.priority = self.PriorityType.CRITICAL
		else:
			raise RuntimeError('Nieznany priorytet')
	
	def setIssueType(self, txt):
		if txt == 'Defect':
			self.issueType = self.IssueTypeType.DEFECT
		elif txt == 'Enhancement':
			self.issueType = self.IssueTypeType.ENHANCEMENT
		elif txt == 'Task':
			self.issueType = self.IssueTypeType.TASK
		else:
			raise RuntimeException('Nieznany typ taska');
	
	def setIssueDate(self, txt):
		self.issueDate = int(time.mktime(datetime.datetime(
			*time.strptime(txt, '%b %d, %Y')[:6]).timetuple()) + 3600 * 12)
	
	def __str__(self):
		return (str(self.iid) + ': ' + self.title + '\n' +
			'Status: ' + str(self.status) +
			', autor: ' + self.author +
			', data: ' + str(self.issueDate) +
			', kategoria: ' + str(self.categoryID) +
			', priority: ' + str(self.priority) +
			', type: ' + str(self.issueType) +
			(', owner: ' + self.owner if self.owner else ''))

def re_link_repl(matchobj):
	return matchobj.group(1).replace('\n', '')

def get_issue_info(iid):
	info = IssueInfo(iid)
	contents = get_cached_url('issue', iid)
	
	m = re.search('<div class="content">(.*?)<div class="issue-comment-signin">', contents, re.DOTALL)
	comments = re.findall('<div class="issue-comment[ a-z-]*" id="ic[0-9]+">(.*?)</div>', str(m.group(1)), re.DOTALL)
	issueContents = []
	issueDate = None
	issueAuthor = None
	for comment in comments:
		m = re.search('<p>(Reported|Comment).*? by (.*?), (.*?)</p>', comment, re.DOTALL)
		commentAuthor = str(m.group(2))
		commentDate = str(m.group(3))
		if not issueDate:
			issueDate = commentDate
		if not issueAuthor:
			issueAuthor = commentAuthor
		
		m = re.search('<pre class="issue-comment-text">(.*?)</pre>', comment, re.DOTALL)
		if not m:
			continue
		commentContents = str(m.group(1))
		
		issueContents.append(commentAuthor + ', ' + commentDate + ':\n' + commentContents)
	issueContents = '\n\n'.join(issueContents)
	issueContents = re.sub('<[aA] [^<>]+>([^<>]+)</a>', re_link_repl, issueContents)
	issueContents = (re.sub('<[^<>]+>', '', issueContents).
		replace('&gt;', '>').replace('&lt;', '<').
		replace('&quot;', '"').
		replace('&amp;', '&'))
	issueContents += '\n\nŹródło: Indefero#' + str(iid)
	info.contents = issueContents
	info.setIssueDate(issueDate)
	info.author = issueAuthor
	if not info.author:
		raise RuntimeError('Brak autora')
	
	m = re.search('class="label"><strong>Type:</strong>(.*?)</a>', contents, re.DOTALL)
	info.setIssueType(m.group(1))
	
	m = re.search('<h1 class="title".*?</a>: (.*?)</h1>', contents, re.DOTALL)
	info.setTitle(str(m.group(1)))
	
	m = re.search('<div id="bd">(.*?)</div>[\n ]+<div id="ft">', contents, re.DOTALL)
	contents = m.group(1)
	
	m = re.search('<p>[\n ]*<strong>Status:</strong> (.*?)</p>', contents, re.DOTALL)
	info.setStatus(str(m.group(1)))
	
	m = re.search('<strong>Owner:</strong> <a .*?>(.*?)</a>', contents, re.DOTALL)
	if m:
		info.owner = m.group(1)
	
	m = re.search('class="label"><strong>Priority:</strong>(.*?)</a>', contents, re.DOTALL)
	info.setPriority(m.group(1))
	
	info.setIssueDate(issueDate)
	
	return info

ids_list = []
for i in range(1, get_pages_no()):
	ids_list.extend(get_list(i))

issue_type_ids = {
	IssueInfo.IssueTypeType.DEFECT: 1,
	IssueInfo.IssueTypeType.ENHANCEMENT: 2,
	IssueInfo.IssueTypeType.TASK: 3,
	IssueInfo.IssueTypeType.COSMETIC: 4,
	}

status_type_ids = {
	IssueInfo.StatusType.NEW: 1,
	IssueInfo.StatusType.ACCEPTED: 3,
	IssueInfo.StatusType.STARTED: 4,
	IssueInfo.StatusType.FIXED: 6,
	}

priority_ids = {
	IssueInfo.PriorityType.LOW: 1,
	IssueInfo.PriorityType.MEDIUM: 2,
	IssueInfo.PriorityType.HIGH: 3,
	IssueInfo.PriorityType.CRITICAL: 4,
	}

def usunogonki(txt):
	return (txt.
		replace('ę', 'e').
		replace('ó', 'o').
		replace('ą', 'a').
		replace('ś', 's').
		replace('ł', 'l').
		replace('ż', 'z').
		replace('ź', 'z').
		replace('ć', 'c').
		replace('ń', 'n').
		replace('Ę', 'E').
		replace('Ó', 'O').
		replace('Ą', 'A').
		replace('Ś', 'S').
		replace('Ł', 'L').
		replace('Ż', 'Z').
		replace('Ź', 'Z').
		replace('Ć', 'C').
		replace('Ń', 'N'))

def user_login(username):
	name = usunogonki(username).split(' ')
	return (name[0][0] + name[1]).lower()

users_existing = {
	'twasilczyk': 1,
	'mjablonski': 2,
	'amurawska': 3,
	'ksakwerda': 4,
	'aflinik': 5,
	'iiuwr': 6,
	'kstosiek': 7
	}
users_new_id = 8
users_new = {}
users_new_sql = []

def user_make_new(user_full):
	global users_new
	global users_new_id
	global users_new_sql

	login = user_login(user_full)
	users_new[login] = users_new_id

	users_new_sql.append('(' +
		str(users_new_id) + ', ' + # user_id
		'"' + login + '", ' + # user_name
		'"' + user_full + '", ' + # real_name
		'1, ' + # notify_type
		'1, ' + # notify_own
		'1, ' + # account_enabled
		'1)') # time_zone

	uid = users_new_id
	users_new_id += 1
	
	return uid

def user_get_id(user_full):
	global users_existing
	global users_new
	
	login = user_login(user_full)
	if login in users_existing:
		uid = users_existing[login]
	elif login in users_new:
		uid = users_new[login]
	else:
		uid = user_make_new(user_full)
	
	return uid

def user_get_id_nice(user_full):
	if (user_full == 'Jan Filipowski' or
		user_full == 'Karol Błażejowski' or
		user_full == 'Jakub Tarnawski' or
		user_full == 'Łukasz Synówka'):
		user_full = 'Instytut IUWr'

	return user_get_id(user_full)

issue_sql = []
assignment_sql = []
issue_new_id = 1
for iid in sorted(ids_list):
	issue = get_issue_info(iid)
	
	if issue.owner:
		assignment_sql.append('(' +
			str(issue_new_id) + ', ' + # task_id
			str(user_get_id(issue.owner)) + ')') # user_id
	
	issue_sql.append('(' +
	str(issue_new_id) + ', ' +
	'1, ' + # project_id
	str(issue_type_ids[issue.issueType]) + ', ' + # task_type
	str(issue.issueDate) + ', ' + # date_opened
	str(user_get_id_nice(issue.author)) + ', ' + # opened_by
	'"' + issue.title.replace('"', '\\"') + '", ' + # item_summary
	'"' + issue.contents.replace('"', '\\"') + '", ' + # detailed_desc
	str(status_type_ids[issue.status]) + ', ' + # item_status
	str(issue.categoryID) + ', ' + # product_category
	'1, ' + # product_version
	'1, ' + # operating_system
	'3, ' + # task_severity
	str(priority_ids[issue.priority]) + # task_priority
	')')
	
	issue_new_id += 1

f = open('issues.sql', 'w')

if len(users_new_sql) > 0:
	f.write('INSERT INTO flyspray_users (' +
		'user_id, ' +
		'user_name, ' +
		'real_name, ' +
		'notify_type, ' +
		'notify_own, ' +
		'account_enabled, ' +
		'time_zone) VALUES\n ' +
		(',\n '.join(users_new_sql)) + ';\n\n')

f.write('TRUNCATE flyspray_tasks;\n');
f.write('INSERT INTO flyspray_tasks (' +
	'task_id, '
	'project_id, ' + # 1
	'task_type, ' +
	'date_opened, ' +
	'opened_by, ' +
	'item_summary, ' +
	'detailed_desc, ' +
	'item_status, ' +
	'product_category, ' +
	'product_version, ' + # 1
	'operating_system, ' + # 1
	'task_severity, ' + # 3
	'task_priority' + # 1-6
	') VALUES\n ' + (',\n '.join(issue_sql)) + ';\n\n')

f.write('TRUNCATE flyspray_assigned;\n');
f.write('INSERT INTO flyspray_assigned (task_id, user_id) VALUES\n ' +
	(',\n '.join(assignment_sql)) + ';\n\n')

f.close()
