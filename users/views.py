from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from wagtail.images.models import Image as WagtailImage

from .models import UserProfile
from .forms import UserRegistrationForm, UserProfileForm

def user_register(request):
    """
    Handle regular user registration.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            
            # Handle profile image if provided
            if 'profile_image' in request.FILES:
                image_file = request.FILES['profile_image']
                wagtail_image = WagtailImage.objects.create(
                    file=image_file,
                    title=f"{user.get_full_name() or user.username} Profile"
                )
                user.user_profile.profile_image = wagtail_image
                user.user_profile.save()
            
            # Authenticate and login the user
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )
            login(request, user)
            
            messages.success(request, "تم إنشاء حسابك بنجاح!")
            return redirect('/')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'users/register.html', context)

def user_login(request):
    """
    Handle regular user login.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, "اسم المستخدم أو كلمة المرور غير صحيحة.")
    
    return render(request, 'users/login.html')

@login_required
def user_logout(request):
    """
    Handle user logout.
    """
    if request.method == 'POST':
        logout(request)
        messages.success(request, "تم تسجيل الخروج بنجاح.")
    
    return redirect('/')

@login_required
def user_profile(request, slug=None):
    """
    Display the user profile.
    """
    # If no slug is provided, display the current user's profile
    if not slug:
        profile = get_object_or_404(UserProfile, user=request.user)
    else:
        profile = get_object_or_404(UserProfile, slug=slug)
    
    context = {
        'profile': profile,
        'is_owner': request.user == profile.user,
    }
    
    return render(request, 'users/profile.html', context)

@login_required
def edit_profile(request):
    """
    Allow users to edit their profile.
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Handle profile image if provided
            if 'profile_image' in request.FILES:
                image_file = request.FILES['profile_image']
                if profile.profile_image:
                    # Update existing image
                    profile.profile_image.file = image_file
                    profile.profile_image.title = f"{request.user.get_full_name() or request.user.username} Profile"
                    profile.profile_image.save()
                else:
                    # Create new image
                    wagtail_image = WagtailImage.objects.create(
                        file=image_file,
                        title=f"{request.user.get_full_name() or request.user.username} Profile"
                    )
                    profile.profile_image = wagtail_image
            
            # Update the profile
            form.save()
            
            # Update user model fields
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            
            messages.success(request, "تم تحديث ملفك الشخصي بنجاح!")
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
    }
    
    return render(request, 'users/edit_profile.html', context)
