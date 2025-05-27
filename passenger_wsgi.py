import sys, os

# Полный путь до директории проекта на сервере
sys.path.insert(0, '/home/pangranby/pangran')

os.environ['DJANGO_SETTINGS_MODULE'] = 'pangran.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
