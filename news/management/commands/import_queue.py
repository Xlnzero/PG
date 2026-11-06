import re
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from news.models import Post, PostPhoto

IMAGE_EXT = {'.jpg', '.jpeg', '.png'}
MAX_PHOTOS = 10


def natural_key(path):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', path.name)]


class Command(BaseCommand):
    help = 'Импорт постов из папок очереди (text.txt + фото) со статусом "в очереди"'

    def add_arguments(self, parser):
        parser.add_argument('path')

    def handle(self, *args, **options):
        root = Path(options['path'])
        if not root.is_dir():
            raise CommandError(f'Папка не найдена: {root}')

        folders = sorted((p for p in root.iterdir() if p.is_dir()), key=natural_key)
        created = 0
        for folder in folders:
            if (folder / 'imported.txt').exists():
                continue
            text_file = folder / 'text.txt'
            photos = sorted(
                (p for p in folder.iterdir() if p.suffix.lower() in IMAGE_EXT),
                key=natural_key,
            )
            if not text_file.exists() or not photos:
                self.stdout.write(f'Пропуск {folder.name}: нет text.txt или фото')
                continue
            if len(photos) > MAX_PHOTOS:
                self.stdout.write(f'{folder.name}: фото больше {MAX_PHOTOS}, беру первые {MAX_PHOTOS}')
                photos = photos[:MAX_PHOTOS]

            lines = text_file.read_text(encoding='utf-8-sig').strip().splitlines()
            if not lines:
                self.stdout.write(f'Пропуск {folder.name}: text.txt пустой')
                continue
            title = lines[0].strip()[:200]
            body = '\n'.join(lines[1:]).strip() or title

            with transaction.atomic():
                post = Post.objects.create(
                    title=title, text=body, status='queued', source='csv',
                )
                for i, photo_path in enumerate(photos):
                    with photo_path.open('rb') as f:
                        photo = PostPhoto(post=post, order=i)
                        photo.image.save(photo_path.name, File(f), save=True)

            (folder / 'imported.txt').write_text(f'post id {post.id}', encoding='utf-8')
            created += 1
            self.stdout.write(f'OK {folder.name}: пост {post.id}, фото {len(photos)}')

        self.stdout.write(f'Готово, создано постов: {created}')
