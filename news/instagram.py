import time
import requests

from django.conf import settings

GRAPH = "https://graph.facebook.com/v26.0"
MAX_CAPTION = 2200  # лимит Instagram на подпись


class InstagramError(Exception):
    pass


def clean(text):
    """Убираем токен из текста ошибки, чтобы он не попал в логи."""
    token = settings.INSTAGRAM_ACCESS_TOKEN
    text = str(text)
    return text.replace(token, "***") if token else text


def _call(method, path, **params):
    params["access_token"] = settings.INSTAGRAM_ACCESS_TOKEN
    try:
        if method == "POST":
            resp = requests.post(f"{GRAPH}/{path}", data=params, timeout=60)
        else:
            resp = requests.get(f"{GRAPH}/{path}", params=params, timeout=60)
        data = resp.json()
    except Exception as e:
        raise InstagramError(f"связь с Instagram: {type(e).__name__}: {clean(e)}")
    if "error" in data:
        err = data["error"]
        raise InstagramError(
            f"Instagram отказал: {err.get('message')} "
            f"(код {err.get('code')}/{err.get('error_subcode')})")
    return data


def _wait_ready(container_id, timeout=90):
    """Ждём, пока Instagram обработает фото (статус FINISHED)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        data = _call("GET", container_id, fields="status_code,status")
        code = data.get("status_code")
        if code == "FINISHED":
            return
        if code in ("ERROR", "EXPIRED"):
            raise InstagramError(f"контейнер {container_id}: {code} {data.get('status', '')}")
        time.sleep(3)
    raise InstagramError(f"контейнер {container_id}: не обработан за {timeout} сек")


def build_caption(post):
    """Подпись = заголовок + текст (хештеги уже внутри текста)."""
    parts = [p for p in (post.title.strip(), post.text.strip()) if p]
    return "\n\n".join(parts)[:MAX_CAPTION]


def publish_post(post):
    """Публикует пост в Instagram: одно фото или карусель до 10 фото."""
    user_id = settings.INSTAGRAM_USER_ID
    site = settings.SITE_URL.rstrip("/")
    urls = [f"{site}{p.image.url}" for p in post.photos.all()][:10]
    if not urls:
        raise InstagramError("у поста нет фото")
    caption = build_caption(post)

    if len(urls) == 1:
        container = _call("POST", f"{user_id}/media",
                          image_url=urls[0], caption=caption)["id"]
    else:
        children = []
        for url in urls:
            child = _call("POST", f"{user_id}/media",
                          image_url=url, is_carousel_item="true")["id"]
            children.append(child)
        for child in children:
            _wait_ready(child)
        container = _call("POST", f"{user_id}/media", media_type="CAROUSEL",
                          children=",".join(children), caption=caption)["id"]

    _wait_ready(container)
    media_id = _call("POST", f"{user_id}/media_publish", creation_id=container)["id"]

    post.instagram_media_id = media_id
    post.published_to_instagram = True
    post.instagram_error = ""
    post.save(update_fields=["instagram_media_id", "published_to_instagram", "instagram_error"])
    return media_id