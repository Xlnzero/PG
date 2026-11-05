import time
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from news.instagram import publish_post, clean
from news.models import Post

QUIET_SECONDS = 60  # ждём после последнего фото альбома


class Command(BaseCommand):
    help = "Публикует новые посты из Telegram в Instagram"

    def add_arguments(self, parser):
        parser.add_argument("--loop", action="store_true",
                            help="работать постоянно, проверка каждые 30 секунд")
        parser.add_argument("--since-hours", type=int, default=3,
                            help="брать только посты не старше N часов")

    def handle(self, *args, **opts):
        if not (settings.INSTAGRAM_ACCESS_TOKEN and settings.INSTAGRAM_USER_ID):
            raise CommandError("Не заданы INSTAGRAM_ACCESS_TOKEN и INSTAGRAM_USER_ID")
        while True:
            self.run_once(opts["since_hours"])
            if not opts["loop"]:
                break
            time.sleep(30)

    def run_once(self, since_hours):
        now = timezone.now()
        posts = Post.objects.filter(
            status="published",
            source="telegram",
            published_to_instagram=False,
            instagram_error="",
            created_at__gte=now - timedelta(hours=since_hours),
            last_photo_at__isnull=False,
            last_photo_at__lte=now - timedelta(seconds=QUIET_SECONDS),
        ).order_by("created_at")
        for post in posts:
            try:
                media_id = publish_post(post)
                self.stdout.write(f"пост #{post.pk}: опубликован в Instagram ({media_id})")
            except Exception as e:
                post.instagram_error = clean(e)[:1000]
                post.save(update_fields=["instagram_error"])
                self.stderr.write(f"пост #{post.pk}: ОШИБКА: {post.instagram_error}")