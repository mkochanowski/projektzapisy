#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

def try_remove(path):
	if os.path.exists(path):
		os.remove(path);

try_remove('log.log')
try_remove('fereol/settings_local.py')

os.chdir('fereol')
os.system('rm -f database/*.sqlite3')
os.system('find -name \'*.pyc\' -exec rm \'{}\' \\;')
os.chdir('search_index')
os.system('rm -f MAIN_LOCK')
os.system('rm -f *.dci')
os.system('rm -f *.dcz')
os.system('rm -f *.pst')
os.system('rm -f *.tiz')
os.system('rm -f *.toc')
os.chdir('..')
os.chdir('..')

################################################################################
# Czyszczenie bazy postgresql.
################################################################################

import ConfigParser
import psycopg2
import string

config = ConfigParser.RawConfigParser()
if not os.path.exists('init.ini'):
	exit()
config.read('init.ini')

dbname = config.get('database', 'name')
dbuser = config.get('database', 'user')
dbpassword = config.get('database', 'password')

if (dbname == '') and (dbuser == '') and (dbpassword == ''):
	exit()

if (dbname == '') or (dbuser == ''):
	print 'Nie podano kompletnych danych do bazy postgresql'
	exit()

conn = psycopg2.connect('dbname=' + dbname + ' user=' + dbuser + ' password=' + dbpassword)
cursor = conn.cursor()

cursor.execute("SELECT table_name FROM information_schema.tables WHERE " +
	"table_schema='public' AND table_type != 'VIEW' " +
	"AND table_name NOT LIKE 'pg_ts_%%'")
couldnt_drop = []
dropped = 0
rows = cursor.fetchall()
for row in rows:
	try:
		cursor.execute('DROP TABLE %s CASCADE' % row[0])
		dropped += 1
	except:
		couldnt_drop.append(row[0])
conn.commit()
conn.close()

if (dropped):
	print 'Usunięto tabel: ' + str(dropped)
if (len(couldnt_drop)):
	print ('Nie usunięto tabel (' + str(len(couldnt_drop)) + '): ' +
		string.join(couldnt_drop, ', '))
