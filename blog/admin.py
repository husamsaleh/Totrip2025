from django.contrib import admin
from wagtail import hooks
from wagtail.admin.panels import FieldPanel
from wagtail.admin.ui.tables import Column, DateColumn
from wagtail.admin.views.generic import IndexView
from .models import BlogCategory, BlogAuthor


class BlogCategoryAdmin(admin.ModelAdmin):
    model = BlogCategory
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')


class BlogAuthorAdmin(admin.ModelAdmin):
    model = BlogAuthor
    list_display = ('name',)
    search_fields = ('name',)


admin.site.register(BlogCategory, BlogCategoryAdmin)
admin.site.register(BlogAuthor, BlogAuthorAdmin)
