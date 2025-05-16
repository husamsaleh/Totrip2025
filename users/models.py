from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from wagtail.images.models import Image as WagtailImage

class UserProfile(models.Model):
    """
    Model for regular user profiles.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    bio = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ForeignKey(
        WagtailImage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.user.username)
        super().save(*args, **kwargs)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create a user profile when a new user is created.
    Only create for non-staff users without a tour guide profile.
    """
    if created and not instance.is_staff and not hasattr(instance, 'tour_guide'):
        # Check if they already have a user profile
        if not hasattr(instance, 'user_profile'):
            UserProfile.objects.create(user=instance)
