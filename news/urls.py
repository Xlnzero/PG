from django.urls import path
from . import views, publish_api

urlpatterns = [
    path('news/api/publish/', publish_api.api_publish, name='api_publish'),
    path('news/api/notify/', publish_api.api_notify, name='api_notify'),
    path('news/<slug:slug>/', views.post_detail, name='news_detail'),
    path('telegram/webhook/', views.telegram_webhook, name='telegram_webhook'),
    path('news/', views.post_list, name='news_list'),
]