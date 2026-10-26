from blog.models import Blog


def create_blog(*, title, content, image=""):
    return Blog.objects.create(title=title, content=content, image=image)


def update_blog(blog, *, title, content, image=""):
    blog.title = title
    blog.content = content
    blog.image = image
    blog.save(update_fields=["title", "content", "image"])
    return blog


def delete_blog(blog):
    blog.delete()
