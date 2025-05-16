from django.contrib import admin
from .models import (
    TourGuide, Language, Certification, Specialty, TourPackage, 
    Location, WorkSchedule, Gallery, Video, Review, Badge, BadgeAssignment
)

class GalleryInline(admin.TabularInline):
    model = Gallery
    extra = 1

class VideoInline(admin.TabularInline):
    model = Video
    extra = 1

class TourPackageInline(admin.TabularInline):
    model = TourPackage
    extra = 1

class WorkScheduleInline(admin.TabularInline):
    model = WorkSchedule
    extra = 1

class BadgeAssignmentInline(admin.TabularInline):
    model = BadgeAssignment
    extra = 1

@admin.register(TourGuide)
class TourGuideAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'is_verified', 'is_featured', 'is_recommended', 'created_at')
    list_filter = ('is_active', 'is_verified', 'is_featured', 'is_recommended')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [GalleryInline, VideoInline, TourPackageInline, WorkScheduleInline, BadgeAssignmentInline]
    actions = ['verify_guides', 'feature_guides', 'recommend_guides', 'deactivate_guides', 'activate_guides']
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'slug', 'profile_image', 'banner_image', 'bio', 'phone_number')
        }),
        ('Professional Information', {
            'fields': ('languages', 'certifications', 'specialties', 'years_of_experience')
        }),
        ('Social Media', {
            'fields': ('website', 'twitter', 'instagram', 'facebook', 'linkedin', 'youtube'),
            'classes': ('collapse',),
        }),
        ('Status', {
            'fields': ('is_active', 'is_verified', 'is_featured', 'is_recommended')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def verify_guides(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} guides were verified successfully.')
    verify_guides.short_description = "Verify selected tour guides"
    
    def feature_guides(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} guides were featured successfully.')
    feature_guides.short_description = "Feature selected tour guides"
    
    def recommend_guides(self, request, queryset):
        updated = queryset.update(is_recommended=True)
        self.message_user(request, f'{updated} guides were recommended successfully.')
    recommend_guides.short_description = "Recommend selected tour guides"
    
    def deactivate_guides(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} guides were deactivated successfully.')
    deactivate_guides.short_description = "Deactivate selected tour guides"
    
    def activate_guides(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} guides were activated successfully.')
    activate_guides.short_description = "Activate selected tour guides"

@admin.register(TourPackage)
class TourPackageAdmin(admin.ModelAdmin):
    list_display = ('title', 'tour_guide', 'price', 'is_active', 'is_featured')
    list_filter = ('is_active', 'is_featured')
    search_fields = ('title', 'description', 'tour_guide__user__username')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    actions = ['activate_packages', 'deactivate_packages', 'feature_packages']
    
    def activate_packages(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} packages were activated.')
    activate_packages.short_description = "Activate selected packages"
    
    def deactivate_packages(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} packages were deactivated.')
    deactivate_packages.short_description = "Deactivate selected packages"
    
    def feature_packages(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} packages were featured.')
    feature_packages.short_description = "Feature selected packages"

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'is_popular')
    list_filter = ('country', 'city', 'is_popular')
    search_fields = ('name', 'city', 'country')
    actions = ['mark_as_popular', 'unmark_as_popular']
    
    def mark_as_popular(self, request, queryset):
        updated = queryset.update(is_popular=True)
        self.message_user(request, f'{updated} locations were marked as popular.')
    mark_as_popular.short_description = "Mark selected locations as popular"
    
    def unmark_as_popular(self, request, queryset):
        updated = queryset.update(is_popular=False)
        self.message_user(request, f'{updated} locations were unmarked as popular.')
    unmark_as_popular.short_description = "Unmark selected locations as popular"

@admin.register(WorkSchedule)
class WorkScheduleAdmin(admin.ModelAdmin):
    list_display = ('tour_guide', 'location', 'start_date', 'end_date')
    list_filter = ('location', 'start_date', 'end_date')
    search_fields = ('tour_guide__user__username', 'location__name')
    date_hierarchy = 'start_date'

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('tour_guide', 'title', 'order', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('tour_guide__user__username', 'title')

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('tour_guide', 'title', 'order', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('tour_guide__user__username', 'title')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('tour_guide', 'author_name', 'rating', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('tour_guide__user__username', 'author_name', 'comment')
    actions = ['approve_reviews', 'disapprove_reviews']

    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} reviews were approved.')
    approve_reviews.short_description = "Approve selected reviews"
    
    def disapprove_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} reviews were disapproved.')
    disapprove_reviews.short_description = "Disapprove selected reviews"

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'color')
    search_fields = ('name', 'description')

@admin.register(BadgeAssignment)
class BadgeAssignmentAdmin(admin.ModelAdmin):
    list_display = ('tour_guide', 'badge', 'assigned_at', 'assigned_by')
    list_filter = ('badge', 'assigned_at')
    search_fields = ('tour_guide__user__username', 'badge__name')
    readonly_fields = ('assigned_at',)

# Register smaller models with simple admin interface
admin.site.register(Language)
admin.site.register(Certification)
admin.site.register(Specialty)
