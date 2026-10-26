from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render

from CRUD import operations

from .forms import BlogForm
from .models import Blog


def blog_list(request):
    return render(request, "blog/blog_list.html", {"blogs": Blog.objects.all()})


def blog_detail(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    Blog.objects.filter(pk=blog.pk).update(likes=F("likes") + 1)
    blog.refresh_from_db(fields=["likes"])
    return render(request, "blog/blog_detail.html", {"blog": blog})


def blog_create(request):
    data = request.POST if request.method == "POST" else None
    form = BlogForm(data)
    if request.method == "POST" and form.is_valid():
        operations.create_blog(**form.cleaned_data)
        return redirect("blog:list")
    return render(request, "blog/blog_form.html", {"form": form})


def blog_update(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    data = request.POST if request.method == "POST" else None
    form = BlogForm(data, instance=blog)
    if request.method == "POST" and form.is_valid():
        operations.update_blog(blog, **form.cleaned_data)
        return redirect("blog:detail", pk=blog.pk)
    return render(request, "blog/blog_form.html", {"form": form, "blog": blog})


def blog_delete(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == "POST":
        operations.delete_blog(blog)
        return redirect("blog:list")
    return render(request, "blog/blog_confirm_delete.html", {"blog": blog})
