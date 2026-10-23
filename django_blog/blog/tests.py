from urllib.parse import quote

from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse

from .models import Blog


class BlogListTests(TestCase):
    def setUp(self):
        self.blog = Blog.objects.create(
            title="Первая статья",
            content="Содержание первой статьи",
        )
        self.url = reverse("blog:list")

    def test_list_returns_success(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_list_uses_expected_template(self):
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "blog/blog_list.html")

    def test_list_contains_blog_title_and_link(self):
        response = self.client.get(self.url)

        self.assertContains(response, self.blog.title)
        self.assertContains(
            response,
            reverse("blog:detail", args=[self.blog.pk]),
        )

    def test_list_context_contains_blog(self):
        response = self.client.get(self.url)

        self.assertIn(self.blog, response.context["blogs"])

    def test_list_renders_artist_photos(self):
        response = self.client.get(self.url)

        for filename in ("Ван Гог.jpg", "Леонардо да Винчи.jpg", "Микеланджело.jpg"):
            self.assertContains(response, f"/static/{quote(filename)}")

    def test_artist_articles_are_seeded_with_photos(self):
        articles = {
            article.title: article.image
            for article in Blog.objects.filter(image__gt="")
        }

        self.assertEqual(
            articles,
            {
                "Винсент ван Гог: жизнь и творчество": "Ван Гог.jpg",
                "Леонардо да Винчи: художник и изобретатель": "Леонардо да Винчи.jpg",
                "Микеланджело: мастер эпохи Возрождения": "Микеланджело.jpg",
            },
        )
        for image in articles.values():
            self.assertIsNotNone(finders.find(image))

    def test_empty_list_has_empty_state(self):
        Blog.objects.all().delete()

        response = self.client.get(self.url)

        self.assertContains(response, "Пока нет статей.")


class BlogDetailTests(TestCase):
    def setUp(self):
        self.blog = Blog.objects.create(
            title="Тестовая статья",
            content="Текст для страницы статьи",
        )
        self.url = reverse("blog:detail", args=[self.blog.pk])

    def test_detail_returns_success_for_existing_blog(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_detail_shows_blog_content_and_id(self):
        response = self.client.get(self.url)

        self.assertContains(response, self.blog.title)
        self.assertContains(response, self.blog.content)
        self.assertContains(response, f'data-blog-id="{self.blog.pk}"')
        self.assertEqual(response.context["blog"].pk, self.blog.pk)

    def test_detail_contains_link_back_to_list(self):
        response = self.client.get(self.url)

        self.assertContains(response, reverse("blog:list"))

    def test_detail_renders_associated_photo(self):
        self.blog.image = "Ван Гог.jpg"
        self.blog.save(update_fields=["image"])

        response = self.client.get(self.url)

        self.assertContains(response, f"/static/{quote('Ван Гог.jpg')}")

    def test_detail_for_missing_id_returns_404(self):
        response = self.client.get(reverse("blog:detail", args=[99999]))

        self.assertEqual(response.status_code, 404)

    def test_new_blog_starts_with_zero_views(self):
        self.assertEqual(self.blog.likes, 0)

    def test_detail_get_increments_views_once(self):
        self.client.get(self.url)
        self.blog.refresh_from_db()

        self.assertEqual(self.blog.likes, 1)

    def test_each_detail_get_increments_views_again(self):
        self.client.get(self.url)
        self.client.get(self.url)
        self.blog.refresh_from_db()

        self.assertEqual(self.blog.likes, 2)
