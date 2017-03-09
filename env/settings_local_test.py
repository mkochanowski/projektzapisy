DEBUG = True
PIPELINE = False
DATABASES = {
     'default' : {
        'ENGINE' : 'django.db.backends.postgresql_psycopg2',
            'NAME' : 'circle_test',
            'PORT' : '5432',
            'USER' : 'ubuntu',
            'HOST' : 'localhost',
            'CHARSET' : 'utf8',
            'USE_UNICODE' : True,
        }
}


