from django.conf import settings

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'django_serialize_model_graph.sqlite'}}
settings.configure(DEBUG=True, DATABASES=DATABASES, INSTALLED_APPS=['tests'])
