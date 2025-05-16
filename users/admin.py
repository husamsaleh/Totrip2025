from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'slug', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('slug', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'slug')
        }),
        ('Profile Info', {
            'fields': ('bio', 'phone_number', 'profile_image')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
