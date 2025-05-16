from django.db import models
from django.shortcuts import render
from .models import BlogPage, BlogCategory

def blog_page_view(request, page):
    """
    Custom function to enhance a blog page with additional context
    - Increases view count
    - Adds related posts
    - Adds all categories
    """

    page.increase_view_count()
    

    related_posts = []
    if page.categories.all():
        category = page.categories.all()[0]  
        related = BlogPage.objects.live().filter(
            categories=category
        ).exclude(
            id=page.id
        ).order_by('-first_published_at')[:3]
        
        related_posts.extend(related)
    
    if len(related_posts) < 3:
        more_posts = BlogPage.objects.live().exclude(
            id=page.id
        ).exclude(
            id__in=[p.id for p in related_posts]
        ).order_by('-first_published_at')[:3-len(related_posts)]
        
        related_posts.extend(more_posts)
    
    all_categories = BlogCategory.objects.all()
    
    page.related_posts = related_posts
    page.all_categories = all_categories
    
