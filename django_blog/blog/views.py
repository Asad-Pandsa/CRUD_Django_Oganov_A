from django.db.models import F
from django.shortcuts import get_object_or_404, render

from .models import Blog


def blog_list(request):
    return render(request, "blog/blog_list.html", {"blogs": Blog.objects.all()})


def blog_detail(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    Blog.objects.filter(pk=blog.pk).update(likes=F("likes") + 1)
    blog.refresh_from_db(fields=["likes"])
    return render(request, "blog/blog_detail.html", {"blog": blog})
