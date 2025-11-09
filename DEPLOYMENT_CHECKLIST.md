# Чеклист для деплоя на сервер

## ✅ Проверка перед деплоем

### 1. Переменные окружения (.env файл)

Убедитесь, что на сервере создан файл `.env` в корневой директории проекта со следующими переменными:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
EMAIL_HOST_USER=your-email@mail.ru
EMAIL_HOST_PASSWORD=your-email-password
```

**ВАЖНО:**
- `.env` файл НЕ должен быть в git (уже добавлен в .gitignore)
- Сгенерируйте новый SECRET_KEY для production
- Укажите реальный домен в ALLOWED_HOSTS
- DEBUG должен быть False в production

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

Убедитесь, что `python-dotenv` установлен.

### 3. Настройка базы данных

```bash
python manage.py migrate
```

### 4. Сборка статических файлов

```bash
python manage.py collectstatic --noinput
```

### 5. Проверка passenger_wsgi.py

Убедитесь, что путь в `passenger_wsgi.py` соответствует реальному пути на сервере:
```python
sys.path.insert(0, '/home/pangranby/pangran')  # Проверьте этот путь!
```

### 6. Проверка .htaccess

Убедитесь, что `.htaccess` содержит:
```
PassengerEnabled on
PassengerAppEnv production
```

### 7. Права доступа

Убедитесь, что у веб-сервера есть права на чтение файлов проекта и запись в:
- `staticfiles/` (после collectstatic)
- `media/` (если используется)
- `db.sqlite3` (если используется SQLite)

### 8. Тестирование

После деплоя проверьте:
- [ ] Сайт открывается
- [ ] Статические файлы загружаются
- [ ] Форма отправки работает
- [ ] Почта отправляется корректно
- [ ] Нет ошибок в логах

### 9. Генерация SECRET_KEY

Для генерации нового SECRET_KEY выполните:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 🔒 Безопасность

- ✅ DEBUG = False в production
- ✅ SECRET_KEY хранится в .env (не в коде)
- ✅ ALLOWED_HOSTS настроен правильно
- ✅ .env файл в .gitignore
- ✅ Настройки безопасности для production включены

## 📧 Настройка почты

Если почта не работает:
1. Проверьте EMAIL_HOST_USER и EMAIL_HOST_PASSWORD в .env
2. Убедитесь, что на mail.ru включена поддержка SMTP
3. Возможно, нужен пароль приложения, а не обычный пароль

## 🐛 Отладка

Если что-то не работает:
1. Проверьте логи веб-сервера
2. Проверьте, что все переменные окружения установлены
3. Убедитесь, что путь в passenger_wsgi.py правильный
4. Проверьте права доступа к файлам



