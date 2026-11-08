import hmac
import os

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .instagram import publish_post, clean
from .models import Post, PostPhoto


@csrf_exempt
@require_POST
def api_publish(request):
    """Приём готовой публикации от диспетчера. Защита: секрет в заголовке."""
    secret = os.environ.get("PUBLISH_API_SECRET", "")
    got = request.headers.get("X-Publish-Secret", "")
    if not secret or not hmac.compare_digest(got.encode("utf-8"), secret.encode("utf-8")):
        return JsonResponse({"ok": False, "error": "forbidden"}, status=403)

    title = request.POST.get("title", "").strip()
    text = request.POST.get("text", "").strip()
    files = request.FILES.getlist("photos")
    if not text or not files:
        return JsonResponse({"ok": False, "error": "нужны text и photos"}, status=400)

    post = Post.objects.create(title=title[:200], text=text, status="published", source="admin")
    for i, f in enumerate(files[:10]):
        PostPhoto.objects.create(post=post, image=f, order=i)

    result = {"ok": True, "post_id": post.pk,
              "url": settings.SITE_URL.rstrip("/") + "/news/" + post.slug + "/"}
    if request.POST.get("instagram") == "1":
        try:
            result["instagram_id"] = publish_post(post)
        except Exception as e:
            post.instagram_error = clean(e)[:1000]
            post.save(update_fields=["instagram_error"])
            result["instagram_error"] = post.instagram_error
    return JsonResponse(result)