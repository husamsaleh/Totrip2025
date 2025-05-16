from django.urls import path
from django.shortcuts import render
from django.http import HttpResponse
from .views import blog_page_view
from .models import BlogIndexPage

app_name = 'blog'

def blog_index(request):
    try:
        blog_index = BlogIndexPage.objects.live().first()
        return blog_index.serve(request)
    except AttributeError:
        return HttpResponse("Blog section is coming soon!")

urlpatterns = [
    path('', blog_index, name='blog_list'),
] 