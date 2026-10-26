from django.urls import path

from . import views


app_name = "blog"

urlpatterns = [
    path("", views.blog_list, name="list"),
    path("create/", views.blog_create, name="create"),
    path("<int:pk>/edit/", views.blog_update, name="update"),
    path("<int:pk>/delete/", views.blog_delete, name="delete"),
    path("<int:pk>/", views.blog_detail, name="detail"),
]
