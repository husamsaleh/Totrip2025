from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.core.paginator import Paginator
from wagtail.images.models import Image as WagtailImage
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import json
import os

from .models import (
    TourGuide, Language, Certification, Specialty, TourPackage, 
    Location, WorkSchedule, Gallery, Video, Review, Badge, BadgeAssignment
)
from .forms import (
    TourGuideRegistrationForm, TourGuideProfileForm, TourPackageForm,
    GalleryForm, VideoForm, WorkScheduleForm
)

def guide_registration(request):
    """
    Handle tour guide registration.
    """
    if request.method == 'POST':
        form = TourGuideRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # Create the user account
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )
            
            # Create tour guide profile
            profile = TourGuide.objects.create(
                user=user,
                phone_number=form.cleaned_data['phone_number'],
                bio=form.cleaned_data.get('bio', '')
            )
            
            # Handle profile image if provided
            if 'profile_image' in request.FILES:
                image_file = request.FILES['profile_image']
                wagtail_image = WagtailImage.objects.create(
                    file=image_file,
                    title=f"{user.get_full_name() or user.username} Profile"
                )
                profile.profile_image = wagtail_image
                profile.save()
            
            # Log the user in
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )
            login(request, user)
            
            messages.success(request, "Your account has been successfully created! Complete your profile to get started.")
            return redirect('tourguides:tourguide_edit_profile')
    else:
        form = TourGuideRegistrationForm()
    
    return render(request, 'tourguides/register.html', {'form': form})

def guide_login(request):
    """
    Handle tour guide login.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Check if user has a tour guide profile
            try:
                tour_guide = TourGuide.objects.get(user=user)
                login(request, user)
                return redirect('tourguides:tourguide_dashboard')
            except TourGuide.DoesNotExist:
                messages.error(request, "You don't have a tour guide profile. Please register as a tour guide.")
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'tourguides/login.html')

@login_required
def guide_dashboard(request):
    """
    Render the dashboard for tour guides
    """
    try:
        # Get the tour guide instance for the current user
        tour_guide = TourGuide.objects.get(user=request.user)
        
        # Get tour packages created by this guide
        packages = TourPackage.objects.filter(tour_guide=tour_guide)
        
        # Get work schedules for this guide
        schedules = WorkSchedule.objects.filter(tour_guide=tour_guide)
        
        # Get gallery images count
        gallery_images_count = Gallery.objects.filter(tour_guide=tour_guide).count()
        
        # Get videos for this guide
        videos = Video.objects.filter(tour_guide=tour_guide).order_by('order', '-created_at')
        videos_count = videos.count()
        
        # Get reviews for this guide
        reviews = Review.objects.filter(tour_guide=tour_guide)
        
        # Calculate average rating
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        avg_rating = round(avg_rating, 1)
        
        context = {
            'tour_guide': tour_guide,
            'packages': packages,
            'schedules': schedules,
            'gallery_count': gallery_images_count,
            'videos': videos,
            'videos_count': videos_count,
            'reviews': reviews,
            'avg_rating': avg_rating,
            'review_count': reviews.count(),
        }
        
        return render(request, 'tourguides/dashboard.html', context)
    
    except TourGuide.DoesNotExist:
        messages.error(request, "You don't have a tour guide profile.")
        return redirect('tourguides:guides_list')

@login_required
def guide_edit_profile(request):
    """
    Allow tour guides to edit their profile.
    """
    tour_guide = get_object_or_404(TourGuide, user=request.user)
    
    if request.method == 'POST':
        form = TourGuideProfileForm(request.POST, request.FILES, instance=tour_guide)
        if form.is_valid():
            # Handle profile image if provided
            if 'profile_image' in request.FILES:
                image_file = request.FILES['profile_image']
                if tour_guide.profile_image:
                    # Update existing image
                    tour_guide.profile_image.file = image_file
                    tour_guide.profile_image.title = f"{request.user.get_full_name() or request.user.username} Profile"
                    tour_guide.profile_image.save()
                else:
                    # Create new image
                    wagtail_image = WagtailImage.objects.create(
                        file=image_file,
                        title=f"{request.user.get_full_name() or request.user.username} Profile"
                    )
                    tour_guide.profile_image = wagtail_image
            
            # Handle banner image if provided
            if 'banner_image' in request.FILES:
                banner_file = request.FILES['banner_image']
                if tour_guide.banner_image:
                    # Update existing image
                    tour_guide.banner_image.file = banner_file
                    tour_guide.banner_image.title = f"{request.user.get_full_name() or request.user.username} Banner"
                    tour_guide.banner_image.save()
                else:
                    # Create new image
                    wagtail_image = WagtailImage.objects.create(
                        file=banner_file,
                        title=f"{request.user.get_full_name() or request.user.username} Banner"
                    )
                    tour_guide.banner_image = wagtail_image
            
            # Save the form
            form.save()
            
            # Update user model fields if provided
            if form.cleaned_data.get('first_name'):
                request.user.first_name = form.cleaned_data['first_name']
            if form.cleaned_data.get('last_name'):
                request.user.last_name = form.cleaned_data['last_name']
            request.user.save()
            
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('tourguides:tourguide_profile', slug=tour_guide.slug)
    else:
        # Populate initial data from user model
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        }
        form = TourGuideProfileForm(instance=tour_guide, initial=initial_data)
    
    context = {
        'form': form,
        'tour_guide': tour_guide,
        'languages': Language.objects.all(),
        'certifications': Certification.objects.all(),
        'specialties': Specialty.objects.all(),
    }
    
    return render(request, 'tourguides/edit_profile.html', context)

def guide_profile(request, slug):
    """
    Public profile view for a tour guide.
    """
    tour_guide = get_object_or_404(TourGuide, slug=slug, is_active=True)
    packages = TourPackage.objects.filter(tour_guide=tour_guide, is_active=True)
    gallery = Gallery.objects.filter(tour_guide=tour_guide).order_by('order')
    videos = Video.objects.filter(tour_guide=tour_guide).order_by('order')
    reviews = Review.objects.filter(tour_guide=tour_guide, is_approved=True)
    schedules = WorkSchedule.objects.filter(
        tour_guide=tour_guide, 
        end_date__gte=timezone.now().date()
    ).order_by('start_date')
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    review_count = reviews.count()
    
    # Get assigned badges
    badges = BadgeAssignment.objects.filter(tour_guide=tour_guide).select_related('badge')
    
    context = {
        'tour_guide': tour_guide,
        'packages': packages,
        'gallery': gallery,
        'videos': videos,
        'reviews': reviews,
        'schedules': schedules,
        'avg_rating': avg_rating,
        'review_count': review_count,
        'badges': badges,
        'is_owner': request.user.is_authenticated and request.user == tour_guide.user,
    }
    
    return render(request, 'tourguides/profile.html', context)


def guides_list(request):
    """
    List all active tour guides.
    """
    guides_query = TourGuide.objects.filter(is_active=True)
    
    # Filter by location if provided
    location_id = request.GET.get('location')
    if location_id:
        guides_query = guides_query.filter(
            Q(schedules__location_id=location_id) | 
            Q(packages__locations__id=location_id)
        ).distinct()
    
    # Filter by specialty if provided
    specialty_id = request.GET.get('specialty')
    if specialty_id:
        guides_query = guides_query.filter(specialties__id=specialty_id)
    
    # Filter by language if provided
    language_id = request.GET.get('language')
    if language_id:
        guides_query = guides_query.filter(languages__id=language_id)
    
    # Featured guides first, then sort by recommended status
    guides = guides_query.annotate(
        review_count=Count('reviews', filter=Q(reviews__is_approved=True)),
        avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True))
    ).order_by('-is_featured', '-is_recommended', '-avg_rating', '-review_count')
    
    # Pagination
    paginator = Paginator(guides, 12)  # Show 12 guides per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'locations': Location.objects.all(),
        'specialties': Specialty.objects.all(),
        'languages': Language.objects.all(),
        'selected_location': location_id,
        'selected_specialty': specialty_id,
        'selected_language': language_id,
    }
    
    return render(request, 'tourguides/guides_list.html', context)


@login_required
def add_tour_package(request):
    """
    Allow tour guides to add a new tour package.
    """
    tour_guide = get_object_or_404(TourGuide, user=request.user)
    
    if request.method == 'POST':
        form = TourPackageForm(request.POST)
        if form.is_valid():
            package = form.save(commit=False)
            package.tour_guide = tour_guide
            package.save()
            form.save_m2m()  # Save many-to-many relationships
            
            messages.success(request, "Tour package added successfully!")
            return redirect('tourguides:tourguide_dashboard')
    else:
        form = TourPackageForm()
    
    context = {
        'form': form,
        'tour_guide': tour_guide,
        'locations': Location.objects.all(),
    }
    
    return render(request, 'tourguides/add_package.html', context)

@login_required
def update_tour_package(request, slug):
    """
    Allow tour guides to update an existing tour package.
    """
    tour_guide = get_object_or_404(TourGuide, user=request.user)
    tour_package = get_object_or_404(TourPackage, slug=slug, tour_guide=tour_guide)
    
    if request.method == 'POST':
        form = TourPackageForm(request.POST, instance=tour_package)
        if form.is_valid():
            package = form.save(commit=False)
            package.save()
            form.save_m2m()  # Save many-to-many relationships
            
            messages.success(request, "Tour package updated successfully!")
            return redirect('tourguides:tourguide_dashboard')
    else:
        form = TourPackageForm(instance=tour_package)
    
    context = {
        'form': form,
        'tour_guide': tour_guide,
        'locations': Location.objects.all(),
        'package': tour_package,
        'is_update': True
    }
    
    return render(request, 'tourguides/add_package.html', context)

@login_required
def delete_tour_package(request, slug):
    """
    Allow tour guides to delete an existing tour package.
    """
    tour_guide = get_object_or_404(TourGuide, user=request.user)
    tour_package = get_object_or_404(TourPackage, slug=slug, tour_guide=tour_guide)
    
    if request.method == 'POST':
        tour_package.delete()
        messages.success(request, "Tour package deleted successfully!")
        return redirect('tourguides:tourguide_dashboard')
    
    context = {
        'tour_guide': tour_guide,
        'package': tour_package
    }
    
    return render(request, 'tourguides/delete_package_confirm.html', context)


@login_required
def add_gallery_image(request):
    """
    Allow tour guides to add gallery images.
    """
    tour_guide = get_object_or_404(TourGuide, user=request.user)
    
    # Check if tour guide already has 5 images
    gallery_count = Gallery.objects.filter(tour_guide=tour_guide).count()
    if gallery_count >= 5:
        messages.error(request, "يمكنك إضافة 5 صور كحد أقصى. يرجى حذف بعض الصور أولاً.")
        return redirect('tourguides:tourguide_gallery')
    
    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES)
        if form.is_valid():
            # Process the uploaded image
            if 'uploaded_image' in request.FILES:
                uploaded_image = request.FILES['uploaded_image']
                
                # Create Wagtail image
                wagtail_image = WagtailImage.objects.create(
                    file=uploaded_image,
                    title=f"{form.cleaned_data.get('title') or 'Gallery Image'} - {tour_guide.user.username}"
                )
                
                # Create gallery entry
                gallery_img = form.save(commit=False)
                gallery_img.tour_guide = tour_guide
                gallery_img.image = wagtail_image
                gallery_img.save()
                
                messages.success(request, "تمت إضافة الصورة بنجاح!")
                return redirect('tourguides:tourguide_gallery')
            else:
                messages.error(request, "يرجى تحديد صورة للتحميل.")
        else:
            messages.error(request, "حدث خطأ. يرجى التحقق من البيانات المدخلة.")
    else:
        form = GalleryForm()
    
    context = {
        'form': form,
        'tour_guide': tour_guide
    }
    
    return render(request, 'tourguides/add_gallery_image.html', context)

@login_required
def update_gallery_image(request, id):
    """
    Allow tour guides to update a gallery image.
    """
    tour_guide = get_object_or_404(TourGuide, user=request.user)
    gallery_image = get_object_or_404(Gallery, id=id, tour_guide=tour_guide)
    
    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES, instance=gallery_image)
        if form.is_valid():
            # Process the uploaded image if provided
            if 'uploaded_image' in request.FILES:
                uploaded_image = request.FILES['uploaded_image']
                
                # Update existing Wagtail image or create new one
                if gallery_image.image:
                    # Update existing image
                    gallery_image.image.file = uploaded_image
                    gallery_image.image.title = f"{form.cleaned_data.get('title') or 'Gallery Image'} - {tour_guide.user.username}"
                    gallery_image.image.save()
                else:
                    # Create new image
                    wagtail_image = WagtailImage.objects.create(
                        file=uploaded_image,
                        title=f"{form.cleaned_data.get('title') or 'Gallery Image'} - {tour_guide.user.username}"
                    )
                    gallery_image.image = wagtail_image
            
            # Save the form
            form.save()
            messages.success(request, "تم تحديث الصورة بنجاح!")
            return redirect('tourguides:tourguide_gallery')
    else:
        form = GalleryForm(instance=gallery_image)
    
    context = {
        'form': form,
        'tour_guide': tour_guide,
        'gallery_image': gallery_image,
        'is_update': True
    }
    
    return render(request, 'tourguides/add_gallery_image.html', context)

@login_required
def delete_gallery_image(request, id):
    """
    Allow tour guides to delete a gallery image.
    """
    tour_guide = get_object_or_404(TourGuide, user=request.user)
    gallery_image = get_object_or_404(Gallery, id=id, tour_guide=tour_guide)
    
    if request.method == 'POST':
        gallery_image.delete()
        messages.success(request, "تم حذف الصورة بنجاح!")
        return redirect('tourguides:tourguide_gallery')
    
    context = {
        'tour_guide': tour_guide,
        'gallery_image': gallery_image
    }
    
    return render(request, 'tourguides/delete_gallery_confirm.html', context)

@login_required
def add_video(request):
    """
    Allow tour guides to add videos.
    """
    tour_guide = get_object_or_404(TourGuide, user=request.user)
    
    if request.method == 'POST':
        form = VideoForm(request.POST)
        if form.is_valid():
            video = form.save(commit=False)
            video.tour_guide = tour_guide
            video.save()
            
            messages.success(request, "Video added successfully!")
            return redirect('tourguides:tourguide_videos')
    else:
        form = VideoForm()
    
    context = {
        'form': form,
        'tour_guide': tour_guide,
    }
    
    return render(request, 'tourguides/add_video.html', context)

@login_required
def update_video(request, id):
    """
    Allow tour guides to update their videos.
    """
    tour_guide = get_object_or_404(TourGuide, user=request.user)
    video = get_object_or_404(Video, id=id, tour_guide=tour_guide)
    
    if request.method == 'POST':
        form = VideoForm(request.POST, instance=video)
        if form.is_valid():
            form.save()
            messages.success(request, "Video updated successfully!")
            return redirect('tourguides:tourguide_videos')
    else:
        form = VideoForm(instance=video)
    
    context = {
        'form': form,
        'tour_guide': tour_guide,
        'video': video,
    }
    
    return render(request, 'tourguides/update_video.html', context)

@login_required
def delete_video(request, id):
    """
    Allow tour guides to delete their videos.
    """
    tour_guide = get_object_or_404(TourGuide, user=request.user)
    video = get_object_or_404(Video, id=id, tour_guide=tour_guide)
    
    if request.method == 'POST':
        video.delete()
        messages.success(request, "Video deleted successfully!")
        return redirect('tourguides:tourguide_videos')
    
    context = {
        'tour_guide': tour_guide,
        'video': video,
    }
    
    return render(request, 'tourguides/delete_video.html', context)

@login_required
def add_schedule(request):
    """
    Allow tour guides to add work schedules.
    """
    tour_guide = get_object_or_404(TourGuide, user=request.user)
    
    if request.method == 'POST':
        # Get form data directly
        location_id = request.POST.get('location')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        notes = request.POST.get('notes', '')
        
        # Checkbox value - will be 'on' if checked, None if unchecked
        is_available = request.POST.get('is_available') == 'on'
        
        if location_id and start_date and end_date:
            try:
                location = Location.objects.get(id=location_id)
                
                # Create schedule
                schedule = WorkSchedule.objects.create(
                    tour_guide=tour_guide,
                    location=location,
                    start_date=start_date,
                    end_date=end_date,
                    notes=notes,
                    is_available=is_available
                )
                
                messages.success(request, "تم إضافة جدول العمل بنجاح!")
                return redirect('tourguides:schedules_list')
            except Location.DoesNotExist:
                messages.error(request, "الموقع المحدد غير موجود.")
        else:
            messages.error(request, "يرجى ملء جميع الحقول المطلوبة.")
    
    context = {
        'tour_guide': tour_guide,
        'locations': Location.objects.all(),
    }
    
    return render(request, 'tourguides/add_schedule.html', context)

def add_review(request, slug):
    """
    Allow users to submit reviews for tour guides.
    """
    tour_guide = get_object_or_404(TourGuide, slug=slug, is_active=True)
    
    if request.method == 'POST':
        author_name = request.POST.get('author_name')
        email = request.POST.get('email', '')
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment')
        
        if author_name and comment:
            review = Review.objects.create(
                tour_guide=tour_guide,
                author_name=author_name,
                email=email,
                rating=min(5, max(1, rating)),
                comment=comment,
                is_approved=False  # Reviews need approval before showing up
            )
            
            messages.success(request, "Thank you for your review! It will be visible after approval.")
        else:
            messages.error(request, "Please provide your name and a comment.")
        
        return redirect('tourguides:tourguide_profile', slug=slug)
    
    return redirect('tourguides:tourguide_profile', slug=slug)

def tourguide_reviews(request, slug):
    """
    Display all approved reviews for a tour guide.
    """
    tour_guide = get_object_or_404(TourGuide, slug=slug, is_active=True)
    reviews = Review.objects.filter(tour_guide=tour_guide, is_approved=True).order_by('-created_at')
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    avg_rating = round(avg_rating, 1)
    
    context = {
        'tour_guide': tour_guide,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_count': reviews.count(),
    }
    
    return render(request, 'tourguides/reviews.html', context)

def similar_guides(request, slug):
    """
    Find similar tour guides based on specialties and locations.
    """
    current_guide = get_object_or_404(TourGuide, slug=slug, is_active=True)
    
    # Get specialties of the current guide
    specialties = current_guide.specialties.all()
    
    # Get locations where the current guide operates
    locations = Location.objects.filter(
        Q(schedules__tour_guide=current_guide) | 
        Q(packages__tour_guide=current_guide)
    ).distinct()
    
    # Find similar guides with similar specialties or locations
    similar_guides = TourGuide.objects.filter(
        Q(specialties__in=specialties) | 
        Q(schedules__location__in=locations) |
        Q(packages__locations__in=locations)
    ).exclude(id=current_guide.id).filter(is_active=True).distinct()
    
    # Order by most similar (most matching specialties and locations)
    similar_guides = similar_guides.annotate(
        matches=Count('specialties', filter=Q(specialties__in=specialties)) +
               Count('schedules', filter=Q(schedules__location__in=locations)) +
               Count('packages', filter=Q(packages__locations__in=locations))
    ).order_by('-matches', '-is_featured', '-is_recommended')[:6]
    
    context = {
        'current_guide': current_guide,
        'similar_guides': similar_guides,
    }
    
    return render(request, 'tourguides/similar_guides.html', context)

@login_required
def dashboard(request):
    """
    Admin dashboard for managing tour guides.
    """
    try:
        tour_guide = TourGuide.objects.get(user=request.user)
    except TourGuide.DoesNotExist:
        # If user is not a tour guide, redirect to guides list
        return redirect('tourguides:guides_list')
    
    # Get tour packages
    packages = TourPackage.objects.filter(tour_guide=tour_guide)
    
    # Get work schedules
    schedules = WorkSchedule.objects.filter(tour_guide=tour_guide).order_by('start_date')
    
    # Get gallery images count
    gallery_count = Gallery.objects.filter(tour_guide=tour_guide).count()
    
    # Get reviews
    reviews = Review.objects.filter(tour_guide=tour_guide).order_by('-created_at')
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'tour_guide': tour_guide,
        'packages': packages,
        'schedules': schedules,
        'gallery_count': gallery_count,
        'reviews': reviews,
        'avg_rating': avg_rating,
    }
    
    return render(request, 'tourguides/dashboard.html', context)

@login_required
def gallery_list(request):
    """
    Display all gallery images for a tour guide.
    """
    tour_guide = get_object_or_404(TourGuide, user=request.user)
    gallery_images = Gallery.objects.filter(tour_guide=tour_guide).order_by('-created_at')
    
    # Calculate image limit usage
    images_count = gallery_images.count()
    images_limit = 5
    images_remaining = max(0, images_limit - images_count)
    
    context = {
        'tour_guide': tour_guide,
        'gallery_images': gallery_images,
        'images_count': images_count,
        'images_limit': images_limit,
        'images_remaining': images_remaining,
    }
    
    return render(request, 'tourguides/gallery_list.html', context)

@login_required
def packages_list(request):
    """
    Display all tour packages for a tour guide.
    """
    tour_guide = get_object_or_404(TourGuide, user=request.user)
    packages = TourPackage.objects.filter(tour_guide=tour_guide).order_by('-created_at')
    
    context = {
        'tour_guide': tour_guide,
        'packages': packages,
    }
    
    return render(request, 'tourguides/packages_list.html', context)

@login_required
def tourguide_videos(request):
    """
    Display all videos for a tour guide.
    """
    tour_guide = get_object_or_404(TourGuide, user=request.user)
    videos = Video.objects.filter(tour_guide=tour_guide).order_by('order', '-created_at')
    
    # Calculate video limit usage
    videos_count = videos.count()
    videos_limit = 10  # Set a reasonable limit
    videos_remaining = max(0, videos_limit - videos_count)
    
    context = {
        'tour_guide': tour_guide,
        'videos': videos,
        'videos_count': videos_count,
        'videos_limit': videos_limit,
        'videos_remaining': videos_remaining,
    }
    
    return render(request, 'tourguides/videos_list.html', context)

@login_required
def schedules_list(request):
    """
    Display all work schedules for a tour guide.
    """
    tour_guide = get_object_or_404(TourGuide, user=request.user)
    
    # Get all schedules for this guide, ordered by start date
    schedules = WorkSchedule.objects.filter(tour_guide=tour_guide).order_by('start_date')
    
    # Separate upcoming and past schedules
    today = timezone.now().date()
    upcoming_schedules = schedules.filter(end_date__gte=today)
    past_schedules = schedules.filter(end_date__lt=today)
    
    context = {
        'tour_guide': tour_guide,
        'upcoming_schedules': upcoming_schedules,
        'past_schedules': past_schedules,
        'schedules_count': schedules.count(),
    }
    
    return render(request, 'tourguides/schedules_list.html', context)

@login_required
def logout_view(request):
    """
    Handle user logout.
    """
    if request.method == 'POST':
        logout(request)
        messages.success(request, "تم تسجيل الخروج بنجاح.")
        
    return redirect('tourguides:guides_list')

@login_required
def update_schedule(request, id):
    """
    Allow tour guides to update their work schedules.
    """
    tour_guide = get_object_or_404(TourGuide, user=request.user)
    schedule = get_object_or_404(WorkSchedule, id=id, tour_guide=tour_guide)
    
    if request.method == 'POST':
        # Get form data directly
        location_id = request.POST.get('location')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        notes = request.POST.get('notes', '')
        
        # Checkbox value - will be 'on' if checked, None if unchecked
        is_available = request.POST.get('is_available') == 'on'
        
        if location_id and start_date and end_date:
            try:
                location = Location.objects.get(id=location_id)
                
                # Update schedule
                schedule.location = location
                schedule.start_date = start_date
                schedule.end_date = end_date
                schedule.notes = notes
                schedule.is_available = is_available
                schedule.save()
                
                messages.success(request, "تم تحديث الجدول بنجاح!")
                return redirect('tourguides:schedules_list')
            except Location.DoesNotExist:
                messages.error(request, "الموقع المحدد غير موجود.")
        else:
            messages.error(request, "يرجى ملء جميع الحقول المطلوبة.")
    
    context = {
        'tour_guide': tour_guide,
        'schedule': schedule,
        'locations': Location.objects.all(),
        'is_update': True
    }
    
    return render(request, 'tourguides/add_schedule.html', context)

@login_required
def delete_schedule(request, id):
    """
    Allow tour guides to delete their work schedules.
    """
    tour_guide = get_object_or_404(TourGuide, user=request.user)
    schedule = get_object_or_404(WorkSchedule, id=id, tour_guide=tour_guide)
    
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, "تم حذف الجدول بنجاح!")
        return redirect('tourguides:schedules_list')
    
    context = {
        'tour_guide': tour_guide,
        'schedule': schedule
    }
    
    return render(request, 'tourguides/delete_schedule_confirm.html', context)

@login_required
@csrf_exempt
def add_specialty(request):
    """Add a new specialty via AJAX request"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name', '').strip()
            
            if not name:
                return JsonResponse({'success': False, 'error': 'اسم التخصص مطلوب'})
                
            # Check if specialty already exists
            specialty, created = Specialty.objects.get_or_create(name=name)
            
            return JsonResponse({
                'success': True,
                'id': specialty.id,
                'name': specialty.name,
                'created': created
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'طلب غير صالح'})

@login_required
@csrf_exempt
def add_language(request):
    """Add a new language via AJAX request"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name', '').strip()
            
            if not name:
                return JsonResponse({'success': False, 'error': 'اسم اللغة مطلوب'})
                
            # Check if language already exists
            language, created = Language.objects.get_or_create(name=name)
            
            return JsonResponse({
                'success': True,
                'id': language.id,
                'name': language.name,
                'created': created
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'طلب غير صالح'})

@login_required
@csrf_exempt
def add_certification(request):
    """Add a new certification via AJAX request"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name', '').strip()
            
            if not name:
                return JsonResponse({'success': False, 'error': 'اسم الشهادة مطلوب'})
                
            # Check if certification already exists
            certification, created = Certification.objects.get_or_create(name=name)
            
            return JsonResponse({
                'success': True,
                'id': certification.id,
                'name': certification.name,
                'created': created
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'طلب غير صالح'})
