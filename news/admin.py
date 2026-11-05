from django.contrib import admin
from .models import Post, PostPhoto


class PostPhotoInline(admin.TabularInline):
    model = PostPhoto
    extra = 3


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'status', 'source',
                    'published_to_instagram', 'published_to_telegram')
    list_filter = ('status', 'source', 'published_to_instagram',
                   'published_to_telegram', 'created_at')
    search_fields = ('title', 'text')
    readonly_fields = ('telegram_message_id', 'telegram_chat_id',
                       'telegram_media_group_id', 'instagram_media_id',
                       'instagram_error', 'last_photo_at')
    inlines = [PostPhotoInline]