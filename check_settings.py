#!/usr/bin/env python
"""
Скрипт для проверки настроек Django перед деплоем на сервер
Запустите: python check_settings.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Загружаем .env файл
BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / '.env'
load_dotenv(env_path)

print("=" * 60)
print("ПРОВЕРКА НАСТРОЕК ДЛЯ ДЕПЛОЯ")
print("=" * 60)
print()

errors = []
warnings = []
success = []

# Проверка .env файла
if not env_path.exists():
    errors.append("❌ Файл .env не найден! Создайте его на основе .env.example")
else:
    success.append("✅ Файл .env найден")

# Проверка SECRET_KEY
secret_key = os.getenv('DJANGO_SECRET_KEY')
if not secret_key:
    errors.append("❌ DJANGO_SECRET_KEY не установлен в .env файле")
elif len(secret_key) < 50:
    warnings.append("⚠️  SECRET_KEY слишком короткий (рекомендуется минимум 50 символов)")
else:
    success.append("✅ SECRET_KEY установлен")

# Проверка DEBUG
debug = os.getenv('DEBUG', 'False').lower()
if debug == 'true':
    warnings.append("⚠️  DEBUG=True - убедитесь, что это для разработки, а не production!")
else:
    success.append("✅ DEBUG=False (production режим)")

# Проверка ALLOWED_HOSTS
allowed_hosts = os.getenv('ALLOWED_HOSTS', '')
if not allowed_hosts:
    errors.append("❌ ALLOWED_HOSTS не установлен в .env файле")
elif 'your-domain.com' in allowed_hosts or 'example.com' in allowed_hosts:
    errors.append("❌ ALLOWED_HOSTS содержит примерные значения! Укажите реальный домен")
else:
    success.append(f"✅ ALLOWED_HOSTS установлен: {allowed_hosts}")

# Проверка EMAIL
email_user = os.getenv('EMAIL_HOST_USER')
email_password = os.getenv('EMAIL_HOST_PASSWORD')

if not email_user:
    warnings.append("⚠️  EMAIL_HOST_USER не установлен - отправка почты не будет работать")
elif 'your-email' in email_user:
    errors.append("❌ EMAIL_HOST_USER содержит примерное значение!")
else:
    success.append("✅ EMAIL_HOST_USER установлен")

if not email_password:
    warnings.append("⚠️  EMAIL_HOST_PASSWORD не установлен - отправка почты не будет работать")
else:
    success.append("✅ EMAIL_HOST_PASSWORD установлен")

# Проверка python-dotenv в requirements.txt
requirements_path = BASE_DIR / 'requirements.txt'
if requirements_path.exists():
    with open(requirements_path, 'r', encoding='utf-8') as f:
        requirements = f.read()
        if 'python-dotenv' in requirements:
            success.append("✅ python-dotenv найден в requirements.txt")
        else:
            errors.append("❌ python-dotenv не найден в requirements.txt")
else:
    errors.append("❌ requirements.txt не найден")

# Проверка passenger_wsgi.py
passenger_wsgi_path = BASE_DIR / 'passenger_wsgi.py'
if passenger_wsgi_path.exists():
    with open(passenger_wsgi_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'load_dotenv' in content:
            success.append("✅ passenger_wsgi.py загружает .env файл")
        else:
            warnings.append("⚠️  passenger_wsgi.py не загружает .env файл")
        if '/home/pangranby/pangran' in content:
            warnings.append("⚠️  Проверьте путь в passenger_wsgi.py - он должен соответствовать реальному пути на сервере")
else:
    warnings.append("⚠️  passenger_wsgi.py не найден")

# Проверка .gitignore
gitignore_path = BASE_DIR / '.gitignore'
if gitignore_path.exists():
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        gitignore = f.read()
        if '.env' in gitignore:
            success.append("✅ .env файл добавлен в .gitignore")
        else:
            errors.append("❌ .env файл НЕ добавлен в .gitignore - это небезопасно!")
else:
    warnings.append("⚠️  .gitignore не найден")

# Вывод результатов
print("РЕЗУЛЬТАТЫ ПРОВЕРКИ:")
print("-" * 60)

if success:
    print("\n✅ УСПЕШНО:")
    for item in success:
        print(f"  {item}")

if warnings:
    print("\n⚠️  ПРЕДУПРЕЖДЕНИЯ:")
    for item in warnings:
        print(f"  {item}")

if errors:
    print("\n❌ ОШИБКИ (требуют исправления):")
    for item in errors:
        print(f"  {item}")

print()
print("=" * 60)

if errors:
    print("❌ Обнаружены ошибки! Исправьте их перед деплоем.")
    sys.exit(1)
elif warnings:
    print("⚠️  Есть предупреждения. Проверьте их перед деплоем.")
    sys.exit(0)
else:
    print("✅ Все проверки пройдены успешно!")
    sys.exit(0)



