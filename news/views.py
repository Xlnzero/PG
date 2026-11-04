from django.shortcuts import render, get_object_or_404
from .models import Post
import hmac
import json
import logging

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .telegram_handler import handle_channel_post

logger = logging.getLogger(__name__)


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, 'news/post_detail.html', {
        'post': post,
        'title': post.title,
        'description': post.text[:160],
    })

@csrf_exempt
@require_POST
def telegram_webhook(request):
    secret = settings.TELEGRAM_WEBHOOK_SECRET
    got = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    if not secret or not hmac.compare_digest(got.encode(), secret.encode()):
        return HttpResponseForbidden()

    try:
        update = json.loads(request.body)
    except ValueError:
        return HttpResponse(status=400)

    msg = update.get("channel_post")
    if msg:
        try:
            result = handle_channel_post(msg)
            logger.info("telegram webhook: %s", result)
        except Exception:
            logger.exception("telegram webhook: ошибка обработки поста")
    return HttpResponse("ok")