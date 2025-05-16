from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'tourguides'

urlpatterns = [
    # Authentication URLs
    path('tourguide/register/', views.guide_registration, name='register'),
    path('tourguide/login/', views.guide_login, name='login'),
    path('tourguide/logout/', views.logout_view, name='logout'),
    
    # Dashboard URLs
    path('tourguide/dashboard/', views.guide_dashboard, name='tourguide_dashboard'),
    path('tourguide/profile/edit/', views.guide_edit_profile, name='tourguide_edit_profile'),
    
    # Package management
    path('tourguide/packages/', views.packages_list, name='packages_list'),
    path('tourguide/packages/add/', views.add_tour_package, name='add_package'),
    path('tourguide/packages/update/<slug:slug>/', views.update_tour_package, name='update_package'),
    path('tourguide/packages/delete/<slug:slug>/', views.delete_tour_package, name='delete_package'),
    
    # Gallery management
    path('tourguide/gallery/', views.gallery_list, name='tourguide_gallery'),
    path('tourguide/gallery/add/', views.add_gallery_image, name='add_gallery_image'),
    path('tourguide/gallery/update/<int:id>/', views.update_gallery_image, name='update_gallery_image'),
    path('tourguide/gallery/delete/<int:id>/', views.delete_gallery_image, name='delete_gallery_image'),
    
    # Video management
    path('tourguide/videos/', views.tourguide_videos, name='tourguide_videos'),
    path('tourguide/videos/list/', views.tourguide_videos, name='videos_list'),
    path('tourguide/videos/add/', views.add_video, name='add_video'),
    path('tourguide/videos/update/<int:id>/', views.update_video, name='update_video'),
    path('tourguide/videos/delete/<int:id>/', views.delete_video, name='delete_video'),
    
    # Work schedule management
    path('tourguide/schedules/add/', views.add_schedule, name='add_schedule'),
    path('tourguide/schedules/', views.schedules_list, name='schedules_list'),
    path('tourguide/schedules/update/<int:id>/', views.update_schedule, name='update_schedule'),
    path('tourguide/schedules/delete/<int:id>/', views.delete_schedule, name='delete_schedule'),
    
    # AJAX Endpoints
    path('api/specialties/add/', views.add_specialty, name='add_specialty'),
    path('api/languages/add/', views.add_language, name='add_language'),
    path('api/certifications/add/', views.add_certification, name='add_certification'),
    
    # Public URLs
    path('guides/', views.guides_list, name='guides_list'),
    path('guides/<slug:slug>/', views.guide_profile, name='tourguide_profile'),
    path('guides/<slug:slug>/review/', views.add_review, name='add_review'),
    path('guides/<slug:slug>/reviews/', views.tourguide_reviews, name='tourguide_reviews'),
    path('guides/<slug:slug>/similar-guides/', views.similar_guides, name='similar_guides'),
] 