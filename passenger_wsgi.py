import sys
import os

# Полный путь до директории проекта на сервере
# ВАЖНО: Измените этот путь на реальный путь на вашем сервере!
project_dir = '/home/pangranby/pangran'
sys.path.insert(0, project_dir)

# Загружаем переменные окружения из .env файла
from dotenv import load_dotenv
env_path = os.path.join(project_dir, '.env')
load_dotenv(env_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'pangran.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
