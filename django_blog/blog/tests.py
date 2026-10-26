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


class BlogCRUDTests(TestCase):
    def setUp(self):
        self.blog = Blog.objects.create(
            title="Исходная статья",
            content="Исходное содержание",
        )

    def test_create_article(self):
        response = self.client.post(
            reverse("blog:create"),
            {
                "title": "Новая статья",
                "content": "Новое содержание",
                "image": "",
            },
        )

        self.assertRedirects(response, reverse("blog:list"))
        self.assertTrue(Blog.objects.filter(title="Новая статья").exists())

    def test_invalid_create_does_not_save_article(self):
        article_count = Blog.objects.count()
        response = self.client.post(
            reverse("blog:create"),
            {"title": "", "content": "", "image": ""},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertEqual(Blog.objects.count(), article_count)

    def test_update_article(self):
        response = self.client.post(
            reverse("blog:update", args=[self.blog.pk]),
            {
                "title": "Обновленная статья",
                "content": "Обновленное содержание",
                "image": "",
            },
        )

        self.assertRedirects(
            response,
            reverse("blog:detail", args=[self.blog.pk]),
        )
        self.blog.refresh_from_db()
        self.assertEqual(self.blog.title, "Обновленная статья")
        self.assertEqual(self.blog.content, "Обновленное содержание")

    def test_delete_requires_post_confirmation(self):
        url = reverse("blog:delete", args=[self.blog.pk])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Blog.objects.filter(pk=self.blog.pk).exists())

        response = self.client.post(url)

        self.assertRedirects(response, reverse("blog:list"))
        self.assertFalse(Blog.objects.filter(pk=self.blog.pk).exists())

    def test_crud_pages_return_404_for_missing_article(self):
        for name in ("update", "delete"):
            with self.subTest(view=name):
                response = self.client.get(reverse(f"blog:{name}", args=[99999]))
                self.assertEqual(response.status_code, 404)
