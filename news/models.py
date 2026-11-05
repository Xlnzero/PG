from django.db import models
from django.utils import timezone
from django.utils.text import slugify

RU_TO_LAT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    'і': 'i', 'ў': 'u',  # белорусские буквы
}


def make_slug(text):
    """Русский и белорусский текст -> латинский слаг для адреса страницы."""
    latin = ''.join(RU_TO_LAT.get(ch, ch) for ch in text.lower())
    return slugify(latin)[:150]

class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('queued', 'В очереди'),
        ('published', 'Опубликован'),
    ]
    SOURCE_CHOICES = [
        ('admin', 'Админка'),
        ('telegram', 'Telegram'),
        ('csv', 'CSV'),
    ]

    title = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    # состояние поста и откуда он пришёл
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default='admin')

    # Telegram: откуда пришёл пост и опубликован ли он в канале
    telegram_message_id = models.BigIntegerField(unique=True, null=True, blank=True)
    telegram_chat_id = models.BigIntegerField(null=True, blank=True)
    telegram_media_group_id = models.CharField(max_length=64, null=True, blank=True, unique=True)
    published_to_telegram = models.BooleanField(default=False)

    # Instagram
    instagram_media_id = models.CharField(max_length=100, null=True, blank=True)
    published_to_instagram = models.BooleanField(default=False)
    instagram_error = models.TextField(blank=True, default='')
    last_photo_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def is_editable_from_telegram(self):
        """Правки из Telegram применяем только в течение первых суток."""
        return timezone.now().date() == self.created_at.date()

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = make_slug(self.title or self.text[:50]) or 'post'
            self.slug = f"{base_slug}-{int(timezone.now().timestamp())}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title or self.text[:50]


class PostPhoto(models.Model):
    """Одно фото поста. У поста их может быть несколько (альбом, карусель)."""
    post = models.ForeignKey(Post, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='news/%Y/%m/')
    order = models.PositiveSmallIntegerField(default=0)
    telegram_file_unique_id = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Фото {self.order} для поста {self.post_id}"