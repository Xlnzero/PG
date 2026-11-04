import time
import requests

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from news.telegram_handler import handle_channel_post, API


class Command(BaseCommand):
    help = "Локальная проверка: опрашивает Telegram и переносит новые посты канала на сайт"

    def handle(self, *args, **options):
        token = settings.TELEGRAM_BOT_TOKEN
        if not token:
            raise CommandError("Не задан TELEGRAM_BOT_TOKEN (см. шаг 1)")

        self.stdout.write("Слушаю канал. Остановить: Ctrl+C")
        offset = None
        while True:
            try:
                params = {"timeout": 30, "allowed_updates": '["channel_post"]'}
                if offset:
                    params["offset"] = offset
                data = requests.get(f"{API}/bot{token}/getUpdates",
                                    params=params, timeout=45).json()
                if not data.get("ok"):
                    self.stderr.write(f"Telegram вернул ошибку: {data.get('description')}")
                    time.sleep(5)
                    continue
                for update in data["result"]:
                    offset = update["update_id"] + 1
                    msg = update.get("channel_post")
                    if not msg:
                        continue
                    try:
                        result = handle_channel_post(msg)
                    except Exception as e:
                        text = str(e).replace(token, "***")
                        result = f"ОШИБКА: {type(e).__name__}: {text}"
                    self.stdout.write(
                        f"[канал {msg['chat']['id']}] сообщение {msg['message_id']}: {result}")
            except KeyboardInterrupt:
                self.stdout.write("Остановлено.")
                break
            except Exception as e:
                text = str(e).replace(token, "***")
                self.stderr.write(f"Сбой связи: {type(e).__name__}: {text}")
                time.sleep(5)