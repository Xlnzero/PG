from django.shortcuts import render, get_object_or_404
from .models import Post
import hmac
import json
import logging
from main.views import menu
from django.core.paginator import Paginator

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
        'menu': menu,
        'title': post.title or 'Новость',
        'description': (post.text or post.title)[:160],
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

def post_list(request):
    posts = Post.objects.filter(status='published').prefetch_related('photos')
    page = Paginator(posts, 12).get_page(request.GET.get('page'))
    return render(request, 'news/post_list.html', {
        'page': page,
        'menu': menu,
        'title': 'Новости Pangran',
        'description': 'Новости и новые работы Pangran в Гродно.',
    })