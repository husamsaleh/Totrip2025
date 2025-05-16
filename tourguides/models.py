from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from wagtail.images.models import Image as WagtailImage
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import re


class TourGuide(models.Model):
    """
    Model representing a tour guide with extended profile information.
    """
    # Basic information
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tour_guide')
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    bio = models.TextField(blank=True)
    profile_image = models.ForeignKey(
        WagtailImage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    banner_image = models.ForeignKey(
        WagtailImage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    phone_number = models.CharField(max_length=20, blank=True)
    
    # Additional information
    languages = models.ManyToManyField('Language', blank=True)
    certifications = models.ManyToManyField('Certification', blank=True)
    specialties = models.ManyToManyField('Specialty', blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    
    # Social media links
    website = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    
    # Status fields
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_recommended = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Tour Guide"
        verbose_name_plural = "Tour Guides"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.user.username)
        super().save(*args, **kwargs)


class Language(models.Model):
    """Model for languages spoken by tour guides."""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, blank=True)
    
    def __str__(self):
        return self.name


class Certification(models.Model):
    """Model for tour guide certifications."""
    name = models.CharField(max_length=255)
    issuing_organization = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name


class Specialty(models.Model):
    """Model for tour guide specialties."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Specialties"
    
    def __str__(self):
        return self.name


class TourPackage(models.Model):
    """
    Model for tour packages offered by tour guides.
    """
    tour_guide = models.ForeignKey(TourGuide, on_delete=models.CASCADE, related_name='packages')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    duration = models.CharField(max_length=100, help_text="E.g., '2 hours', '1 day'")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    locations = models.ManyToManyField('Location', related_name='packages')
    included_services = models.TextField(blank=True, help_text="What's included in the package")
    excluded_services = models.TextField(blank=True, help_text="What's not included in the package")
    max_people = models.PositiveIntegerField(default=1)
    
    # Status fields
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Location(models.Model):
    """
    Model for locations where tour guides operate.
    """
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=100, default="Saudi Arabia")
    city = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_popular = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name}, {self.city}"


class WorkSchedule(models.Model):
    """
    Model for tour guide work schedules.
    """
    tour_guide = models.ForeignKey(TourGuide, on_delete=models.CASCADE, related_name='schedules')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='schedules')
    start_date = models.DateField()
    end_date = models.DateField()
    notes = models.TextField(blank=True)
    is_available = models.BooleanField(default=True, help_text="Whether the guide is available for booking during this time")
    
    def __str__(self):
        return f"{self.tour_guide} - {self.location} ({self.start_date} to {self.end_date})"


class Gallery(models.Model):
    """
    Model for tour guide gallery images.
    """
    tour_guide = models.ForeignKey(TourGuide, on_delete=models.CASCADE, related_name='gallery')
    image = models.ForeignKey(
        WagtailImage,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='+'
    )
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Galleries"
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.tour_guide} - {self.title or 'Image'}"


class Video(models.Model):
    """
    Model for tour guide videos, supporting YouTube embeds.
    """
    tour_guide = models.ForeignKey(TourGuide, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=255)
    youtube_url = models.URLField(help_text="Full YouTube video URL")
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.title
    
    def get_youtube_id(self):
        """
        Extract YouTube video ID from the URL.
        Works with regular YouTube URLs, shortened URLs, and embed URLs.
        """
        youtube_regex = r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
        match = re.search(youtube_regex, self.youtube_url)
        if match:
            return match.group(1)
        return None
    
    def get_embed_url(self):
        """
        Return the embed URL for the YouTube video.
        """
        video_id = self.get_youtube_id()
        if video_id:
            return f"https://www.youtube.com/embed/{video_id}"
        return None
    
    def get_thumbnail_url(self):
        """
        Return the thumbnail URL for the YouTube video.
        """
        video_id = self.get_youtube_id()
        if video_id:
            return f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"
        return None


class Review(models.Model):
    """
    Model for client reviews of tour guides.
    """
    tour_guide = models.ForeignKey(TourGuide, on_delete=models.CASCADE, related_name='reviews')
    author_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review by {self.author_name} for {self.tour_guide}"


class Badge(models.Model):
    """
    Model for badges that can be awarded to tour guides.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True, help_text="Font Awesome icon class")
    color = models.CharField(max_length=20, blank=True, help_text="Tailwind CSS color class")
    
    def __str__(self):
        return self.name


class BadgeAssignment(models.Model):
    """
    Model for assigning badges to tour guides.
    """
    tour_guide = models.ForeignKey(TourGuide, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        unique_together = ['tour_guide', 'badge']
    
    def __str__(self):
        return f"{self.badge.name} for {self.tour_guide}"
