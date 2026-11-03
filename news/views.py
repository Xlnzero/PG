from django.shortcuts import render, get_object_or_404
from .models import Post


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, 'news/post_detail.html', {
        'post': post,
        'title': post.title,
        'description': post.text[:160],
    })