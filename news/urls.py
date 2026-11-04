from django.urls import path
from . import views

urlpatterns = [
    path('news/<slug:slug>/', views.post_detail, name='news_detail'),
    path('telegram/webhook/', views.telegram_webhook, name='telegram_webhook'),
]