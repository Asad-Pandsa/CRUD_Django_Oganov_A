from django import forms

from .models import Blog


class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ("title", "content", "image")
        widgets = {"content": forms.Textarea(attrs={"rows": 8})}
