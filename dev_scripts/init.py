#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import json
import ConfigParser
import datetime
import shutil
from django.utils.hashcompat import sha_constructor
from getpass import getpass
from random import randint
from string import join

SOURCE_DIR = 'fereol'

def bool_input(prompt):
	while True:
		answer = raw_input(prompt).lower()
		if answer == 't' or answer == 'y':
			return True
		if answer == 'n':
			return False

def gen_hash(password):
	salt = hex(randint(0, 0xFFFFF))[2:]
	sha_hash = sha_constructor(salt + password).hexdigest()
	return 'sha1$' + salt + '$' + sha_hash

def option_input(prompt, options, default = None):
	prompt += ' [' + join(options, '/') + ']'
	if default:
		prompt += ' (domyślnie ' + default + ')'
	prompt += ':'
	while True:
		answer = raw_input(prompt).lower()
		if answer in options:
			return answer
		if answer == '' and default:
			return default

if (os.path.exists(SOURCE_DIR + '/database/db.sqlite3') or
	os.path.exists(SOURCE_DIR + '/settings_local.py')):
	print ('Aplikacja jest już (przynajmniej częściowo) zainicjowana. ' +
		'Aby kontynuować, uruchom skrypt czyszczący.')
	exit()

if not os.path.exists('init-data'):
	os.mkdir('init-data')

################################################################################
# Zbieranie stałych informacji konfiguracyjnych.
################################################################################

config = ConfigParser.RawConfigParser()
if os.path.exists('init.ini'):
	config.read('init.ini')
else:
	print '\033[34m' + 'Konfiguracja wstępna' + '\033[0m'

	print '\033[90m' + 'Ustawienia repozytorium' + '\033[0m'
	config.add_section('source')
	config.set('source', 'dir', 'fereol')
	config.set('source', 'branch', raw_input('Nazwa brancha: '))
	
	print '\033[90m' + 'Ustawienia admina' + '\033[0m'
	config.add_section('super-user')
	config.set('super-user', 'login', raw_input('Login: '))

	password = getpass('Hasło: ')
	if (getpass('Powtórz hasło: ') != password):
		print 'Podane hasła się nie zgadzają'
		exit()

	config.set('super-user', 'hash', gen_hash(password))
	config.set('super-user', 'email', raw_input('Email: '))
	config.set('super-user', 'first-name', raw_input('Imię: '))
	config.set('super-user', 'last-name', raw_input('Nazwisko: '))
	config.set('super-user', 'matricula', int(raw_input('Numer indeksu: ')))

	print '\033[90m' + 'Ustawienia aplikacji' + '\033[0m'
	config.add_section('local-settings')
	config.set('local-settings', 'domain', raw_input('Podaj domenę (lub pusty, jeżeli nie ustawiać): ').strip().strip('.'))
	config.set('local-settings', 'debug', bool_input('Czy włączyć tryb debug (t/n): '))
	config.set('local-settings', 'logging', bool_input('Czy włączyć logowanie do pliku (t/n): '))

	print '\033[90m' + 'Ustawienia bazy danych' + '\033[0m'
	config.add_section('database')
	config.set('database', 'default', option_input('Domyślna baza danych (będzie można później wybrać inną)', ['sqlite', 'pgsql']))
	config.set('database', 'name', raw_input('Nazwa bazy postgresql (jeżeli używane):'))
	config.set('database', 'user', raw_input('Nazwa użytkownika postgresql (jeżeli używane):'))
	config.set('database', 'password', raw_input('Hasło użytkownika postgresql (jeżeli używane):'))

	with open('init.ini', 'wb') as initini:
		config.write(initini)

################################################################################
# Zbieranie zmiennych informacji konfiguracyjnych.
################################################################################

print '\033[34m' + 'Konfiguracja instancji' + '\033[0m'

selected_db = option_input('Baza danych do zainicjowania', ['sqlite', 'pgsql'],
	config.get('database', 'default'))

config_dbsqlite = selected_db == 'sqlite'

################################################################################
# Inicjalizacja bazy - syncdb.
################################################################################

with open('init-data/init.in', 'w') as datain:
	datain.write("no\n") # pytanie: czy chcesz utworzyć superusera

################################################################################
# Inicjalizacja bazy - fixtures.
################################################################################

with open('init-data/init.json', 'w') as datajson:
	fixture = [
		{
			'pk': 1,
			'model': 'users.employee',
			'fields': {
				'receive_mass_mail_offer': True,
				'user': 1
			}
		},
		{
			'pk': 1,
			'model': 'users.student',
			'fields': {
				'matricula': int(config.get('super-user', 'matricula')),
				'user': 1
			}
		}
	]
	datajson.write(json.dumps(fixture));

################################################################################
# Inicjalizacja bazy - SQL.
################################################################################

with open('init-data/early-init.sql', 'w') as datasql:
	sql_now = 'now()'
	sql_true = 'true'
	if config_dbsqlite:
		sql_now = 'datetime(\'now\')'
		sql_true = '1'
	
	datasql.write('INSERT INTO auth_user (' +
		'id, username, first_name, last_name, email, password, is_staff, ' +
		'is_active, is_superuser, last_login, date_joined) VALUES (1,' +
		'\'' + config.get('super-user', 'login') + '\', ' +
		'\'' + config.get('super-user', 'first-name') + '\', ' +
		'\'' + config.get('super-user', 'last-name') + '\', ' +
		'\'' + config.get('super-user', 'email') + '\', ' +
		'\'' + config.get('super-user', 'hash') + '\', ' +
		sql_true + ', ' + sql_true + ', ' + sql_true + ', ' + 
		sql_now + ', ' + sql_now + ');\n')

with open('init-data/init.sql', 'w') as datasql:
	school_year = int(datetime.date.today().strftime('%Y'))
	month = int(datetime.date.today().strftime('%m'))
	if (month <= 7):
		school_year -= 1
	
	semester_beginning = semester_ending = None
	
	is_winter_semester = (month > 7 or month == 1)
	if is_winter_semester:
		semester_beginning = str(school_year) + '-10-01'
		semester_ending = str(school_year + 1) + '-02-02'
	else:
		semester_beginning = str(school_year + 1) + '-02-26'
		semester_ending = str(school_year + 1) + '-06-21'
	
	next_week = 'datetime("now", "+7 day")'
	prev_week = 'datetime("now", "-7 day")'
	if not config_dbsqlite:
		semester_beginning += ' 0:00:00'
		semester_ending += ' 0:00:00'
		next_week = 'now() + interval \'1 week\''
		prev_week = 'now() - interval \'1 week\''
	
	datasql.write('UPDATE subjects_semester SET ' +
		'year = ' + str(school_year) +
		', records_opening = ' + prev_week +
		', records_closing = ' + next_week +
		', semester_beginning = \'' + semester_beginning + '\'' +
		', semester_ending = \'' + semester_ending + '\'' +
		# TODO: jak będą uzupełnione grupy w semestrze zimowym, dać wybieranie 100/101, aktualizację obu semestrów
		' WHERE id = 100;\n')
	
	domain = config.get('local-settings', 'domain')
	if domain:
		domain = ', domain = \'' + domain + '\''
	datasql.write('UPDATE django_site SET name = \'Fereol\'' + domain + ' WHERE id = 1;\n')

################################################################################
# settings_local.py
################################################################################

with open('init-data/settings_local.py', 'w') as local:
	local.write('DEBUG = ' + str(config.get('local-settings', 'debug') == 'True') + '\n')
	local.write('TEMPLATE_DEBUG = DEBUG\n\n')
	
	domain = config.get('local-settings', 'domain')
	if domain:
		local.write('SESSION_COOKIE_DOMAIN = \'.' + domain + '\'\n\n')
	
	logging = config.get('local-settings', 'logging') == 'True'
	if logging:
		local.write('LOG_FILE = os.path.join(PROJECT_PATH, \'../log.log\')\n')
		local.write('LOG_LEVEL = logging.NOTSET\n')
		local.write('INTERNAL_IPS = (\'127.0.0.1\',)\n')
		local.write('logging.basicConfig(level=LOG_LEVEL, ' +
			'filename=LOG_FILE, ' +
			'format = \'%(asctime)s | %(levelname)s | %(message)s\')\n\n')
	
	if not config_dbsqlite: #pgsql
		local.write('DATABASE_ENGINE = \'postgresql_psycopg2\'\n')
		local.write('DATABASE_NAME = \'' + config.get('database', 'name') + '\'\n')
		local.write('DATABASE_USER = \'' + config.get('database', 'user') + '\'\n')
		local.write('DATABASE_PASSWORD = \'' + config.get('database', 'password') + '\'\n')
		local.write('DATABASE_HOST = \'\'\n')
		local.write('DATABASE_PORT = \'\'\n')

################################################################################
# Pobieranie kodu źródłowego.
################################################################################

SOURCE_DIR = config.get('source', 'dir')

if not os.path.exists(SOURCE_DIR):
	os.system('git clone git@iiuwr.indefero.net:iiuwr/fereol.git ' + SOURCE_DIR)
	os.chdir('fereol')
	os.system('git checkout ' + config.get('source', 'branch'))
	os.chdir('..')

################################################################################
# Instalacja.
################################################################################

shutil.copyfile('init-data/settings_local.py', SOURCE_DIR + '/settings_local.py')
os.chdir(SOURCE_DIR)
os.system('python manage.py syncdb < ../init-data/init.in')
os.system('python manage.py migrate')
if not config_dbsqlite:
	print '\033[91m' + 'Podaj hasło do bazy postgresql' + '\033[0m'
os.system('python manage.py dbshell < ../init-data/early-init.sql')
os.system('python manage.py loaddata ../init-data/init.json')
os.system('python manage.py loaddata database/fixtures/initial_data.json')
if not config_dbsqlite:
	print '\033[91m' + 'Podaj hasło do bazy postgresql' + '\033[0m'
os.system('python manage.py dbshell < ../init-data/init.sql')
os.chdir('..')

################################################################################
# Czyszczenie.
################################################################################

if True:
	os.chdir('init-data')
	os.remove('init.in');
	os.remove('init.json');
	os.remove('early-init.sql');
	os.remove('init.sql');
	os.remove('settings_local.py');
	os.chdir('..')
	os.rmdir('init-data')
