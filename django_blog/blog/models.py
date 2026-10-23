from django.db import models


class Blog(models.Model):
    title = models.CharField("Заголовок", max_length=200)
    content = models.TextField("Содержание")
    image = models.CharField("Фотография", max_length=255, blank=True)
    likes = models.PositiveIntegerField("Просмотры", default=0)

    def __str__(self):
        return self.title
