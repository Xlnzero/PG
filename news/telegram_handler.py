import requests
from datetime import datetime, timezone as dt_timezone

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction

from .models import Post, PostPhoto

API = "https://api.telegram.org"


def _download_photo(file_id):
    """Скачивает фото с серверов Telegram и возвращает его байты."""
    token = settings.TELEGRAM_BOT_TOKEN
    info = requests.get(f"{API}/bot{token}/getFile",
                        params={"file_id": file_id}, timeout=30).json()
    if not info.get("ok"):
        raise RuntimeError(f"getFile не удался: {info.get('description')}")
    file_path = info["result"]["file_path"]
    resp = requests.get(f"{API}/file/bot{token}/{file_path}", timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"скачивание фото не удалось, код {resp.status_code}")
    return resp.content


def handle_channel_post(msg):
    """Новый пост из канала -> запись Post (+ фото) на сайте."""
    chat_id = msg["chat"]["id"]
    allowed = settings.TELEGRAM_CHANNEL_ID
    if allowed and str(chat_id) != str(allowed):
        return "пропущено: другой канал"

    message_id = msg["message_id"]
    group_id = msg.get("media_group_id")  # общий номер у фото одного альбома
    caption = (msg.get("caption") or msg.get("text") or "").strip()
    photo_sizes = msg.get("photo")

    with transaction.atomic():
        post = None
        if group_id:
            post = Post.objects.filter(telegram_chat_id=chat_id,
                                       telegram_media_group_id=group_id).first()

        if post is None and Post.objects.filter(telegram_message_id=message_id).exists():
            return "пропущено: уже обработан"

        if post is None:
            title, _, rest = caption.partition("\n")
            post = Post.objects.create(
                title=title.strip()[:200],
                text=rest.strip(),
                created_at=datetime.fromtimestamp(msg["date"], tz=dt_timezone.utc),
                status="published",
                source="telegram",
                telegram_message_id=message_id,
                telegram_chat_id=chat_id,
                telegram_media_group_id=group_id,
                published_to_telegram=True,  # пост уже лежит в канале
            )
        elif caption and not post.title:
            # подпись альбома может прийти не с первым фото
            title, _, rest = caption.partition("\n")
            post.title = title.strip()[:200]
            post.text = rest.strip()
            post.save()

        if photo_sizes:
            biggest = photo_sizes[-1]  # самый большой размер
            unique_id = biggest["file_unique_id"]
            if post.photos.filter(telegram_file_unique_id=unique_id).exists():
                return "пропущено: это фото уже есть"
            content = _download_photo(biggest["file_id"])
            photo = PostPhoto(post=post, order=post.photos.count(),
                              telegram_file_unique_id=unique_id)
            photo.image.save(f"tg_{unique_id}.jpg", ContentFile(content), save=True)

    return f"ок: пост #{post.pk}, фото: {post.photos.count()}"