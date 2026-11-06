import json

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from news.instagram import publish_post, clean
from news.models import Post


def tg_clean(text):
    """Убираем токен бота из текста ошибки."""
    token = settings.TELEGRAM_BOT_TOKEN
    text = str(text)
    return text.replace(token, "***") if token else text


def tg_call(method, data, files=None):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/{method}"
    try:
        resp = requests.post(url, data=data, files=files, timeout=120)
        result = resp.json()
    except Exception as e:
        raise RuntimeError(f"связь с Telegram: {type(e).__name__}: {tg_clean(e)}")
    if not result.get("ok"):
        raise RuntimeError(f"Telegram отказал: {result.get('description')}")
    return result


def send_to_telegram(post):
    chat_id = settings.TELEGRAM_CHANNEL_ID
    photos = list(post.photos.all())[:10]
    title = (post.title or "").strip()
    caption = title[:1024]
    opened = []
    try:
        if len(photos) == 1:
            f = open(photos[0].image.path, "rb")
            opened.append(f)
            tg_call("sendPhoto", {"chat_id": chat_id, "caption": caption}, {"photo": f})
        elif photos:
            media, files = [], {}
            for i, p in enumerate(photos):
                f = open(p.image.path, "rb")
                opened.append(f)
                files[f"photo{i}"] = f
                item = {"type": "photo", "media": f"attach://photo{i}"}
                if i == 0 and caption:
                    item["caption"] = caption
                media.append(item)
            tg_call("sendMediaGroup", {"chat_id": chat_id, "media": json.dumps(media)}, files)
    finally:
        for f in opened:
            f.close()
    body = (post.text or "").strip()
    if body and body != title:
        tg_call("sendMessage", {"chat_id": chat_id, "text": body[:4096]})


class Command(BaseCommand):
    help = "Публикует следующий пост из очереди: сайт, Telegram, Instagram"

    def add_arguments(self, parser):
        parser.add_argument("--skip-telegram", action="store_true")
        parser.add_argument("--skip-instagram", action="store_true")

    def handle(self, *args, **opts):
        if not opts["skip_telegram"] and not (settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHANNEL_ID):
            raise CommandError("Не заданы TELEGRAM_BOT_TOKEN и TELEGRAM_CHANNEL_ID")
        if not opts["skip_instagram"] and not (settings.INSTAGRAM_ACCESS_TOKEN and settings.INSTAGRAM_USER_ID):
            raise CommandError("Не заданы INSTAGRAM_ACCESS_TOKEN и INSTAGRAM_USER_ID")

        post = Post.objects.filter(status="queued").order_by("id").first()
        if not post:
            self.stdout.write("Очередь пуста")
            return

        post.status = "published"
        post.created_at = timezone.now()
        post.save(update_fields=["status", "created_at"])
        self.stdout.write(f"пост #{post.pk}: опубликован на сайте ({post.slug})")

        if not opts["skip_telegram"]:
            try:
                send_to_telegram(post)
                post.published_to_telegram = True
                post.save(update_fields=["published_to_telegram"])
                self.stdout.write(f"пост #{post.pk}: отправлен в Telegram")
            except Exception as e:
                self.stderr.write(f"пост #{post.pk}: Telegram ОШИБКА: {tg_clean(e)[:500]}")

        if not opts["skip_instagram"]:
            try:
                media_id = publish_post(post)
                self.stdout.write(f"пост #{post.pk}: опубликован в Instagram ({media_id})")
            except Exception as e:
                post.instagram_error = clean(e)[:1000]
                post.save(update_fields=["instagram_error"])
                self.stderr.write(f"пост #{post.pk}: Instagram ОШИБКА: {post.instagram_error}")
