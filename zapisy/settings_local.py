DEBUG = True
TEMPLATE_DEBUG = True
PIPELINE = False
DATABASES = {
     'default' : {
        'ENGINE' : 'django.db.backends.postgresql_psycopg2',
            'NAME' : 'fereol',
            'PORT' : '5432',
            'USER' : 'fereol',
            'PASSWORD' : 'fereolpass',
            'HOST' : 'localhost',
            'CHARSET' : 'utf8',
            'USE_UNICODE' : True,
        } 
}

# Changed in Django 1.8.16: with DEBUG = True
# the Host header is still checked
ALLOWED_HOSTS += ['localhost', '127.0.0.1']
