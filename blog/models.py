from django.db import models
from django import forms
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet


class BlogIndexPage(Page):
    intro = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]
    
    def get_context(self, request):
        context = super().get_context(request)
        
        blogpages = BlogPage.objects.live().order_by('-first_published_at')
        
        tag = request.GET.get('tag')
        if tag:
            blogpages = blogpages.filter(tags__name=tag)
            
        category = request.GET.get('category')
        if category:

            blogpages = blogpages.filter(categories__slug=category)
            
        search_query = request.GET.get('query', None)
        if search_query:
            blogpages = blogpages.search(search_query)
            
        paginator = Paginator(blogpages, 9)  
        page = request.GET.get('page')
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
            
        sort_by = request.GET.get('sort_by', 'recent')
        if sort_by == 'recent':
            posts = paginator.page(posts.number)  
        elif sort_by == 'oldest':
            blogpages = BlogPage.objects.live().order_by('first_published_at')
            if tag:
                blogpages = blogpages.filter(tags__name=tag)
            if category:
                blogpages = blogpages.filter(categories__slug=category)
            paginator = Paginator(blogpages, 9)
            posts = paginator.page(1)  
        elif sort_by == 'popular':
            blogpages = BlogPage.objects.live().order_by('-view_count', '-first_published_at')
            if tag:
                blogpages = blogpages.filter(tags__name=tag)
            if category:
                blogpages = blogpages.filter(categories__slug=category)
            paginator = Paginator(blogpages, 9)
            posts = paginator.page(1)  
            
        context['posts'] = posts
        context['categories'] = BlogCategory.objects.all()
        
        categories_with_count = []
        for cat in context['categories']:
            categories_with_count.append({
                'name': cat.name,
                'slug': cat.slug,
                'count': BlogPage.objects.live().filter(categories__slug=cat.slug).count()
            })
        context['categories_with_count'] = categories_with_count
        
        context['search_query'] = search_query
        context['current_tag'] = tag
        

        if 'category' in request.GET:
            context['current_category'] = category
        else:
            context['current_category'] = None
            
        context['current_sort'] = sort_by
        
        return context


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )


class BlogPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    categories = ParentalManyToManyField('blog.BlogCategory', blank=True)
    author = models.ForeignKey(
        'blog.BlogAuthor',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    read_time = models.PositiveIntegerField(default=5, help_text="Approximate read time in minutes")
    view_count = models.PositiveIntegerField(default=0, editable=False)
    
    def main_image(self):
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None
            
    def increase_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def serve(self, request):
        """Override the default serve method to add custom context"""
        context = super().get_context(request)
        
        self.increase_view_count()
        
        related_posts = []
        if self.categories.all():
            category = self.categories.all()[0]  
            related = BlogPage.objects.live().filter(
                categories=category
            ).exclude(
                id=self.id
            ).order_by('-first_published_at')[:3]
            
            related_posts.extend(related)
        
        if len(related_posts) < 3:
            more_posts = BlogPage.objects.live().exclude(
                id=self.id
            ).exclude(
                id__in=[p.id for p in related_posts]
            ).order_by('-first_published_at')[:3-len(related_posts)]
            
            related_posts.extend(more_posts)
        
        all_categories = BlogCategory.objects.all()
        
        context['related_posts'] = related_posts
        context['all_categories'] = all_categories
        
        return render(request, self.template, context)
            
    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]
    
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('date'),
            FieldPanel('tags'),
            FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
            FieldPanel('author'),
        ], heading="Blog information"),
        FieldPanel('featured_image'),
        FieldPanel('intro'),
        FieldPanel('body'),
        FieldPanel('read_time'),
        InlinePanel('gallery_images', label="Gallery images"),
    ]


class BlogPageGalleryImage(Orderable):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)
    
    panels = [
        FieldPanel('image'),
        FieldPanel('caption'),
    ]


@register_snippet
class BlogCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=80)
    
    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
    ]
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Blog Category"
        verbose_name_plural = "Blog Categories"
        ordering = ['name']


@register_snippet
class BlogAuthor(models.Model):
    name = models.CharField(max_length=255)
    profile_image = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )
    bio = RichTextField(blank=True)
    
    panels = [
        FieldPanel('name'),
        FieldPanel('profile_image'),
        FieldPanel('bio'),
    ]
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Blog Author"
        verbose_name_plural = "Blog Authors"
