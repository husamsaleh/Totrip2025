from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'

    def ready(self):
        from .models import BlogPage
        from .views import blog_page_view
        

        BlogPage.get_context = blog_page_view
