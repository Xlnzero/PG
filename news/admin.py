from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'published_to_instagram')
    list_filter = ('published_to_instagram', 'created_at')
    search_fields = ('title', 'text')
    readonly_fields = ('telegram_message_id', 'telegram_chat_id', 'instagram_media_id')