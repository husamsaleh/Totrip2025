from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from .models import (
    TourGuide, TourPackage, Gallery, Video, WorkSchedule,
    Language, Certification, Specialty, Location
)

class TourGuideRegistrationForm(UserCreationForm):
    """
    Form for tour guide registration, extending Django's UserCreationForm.
    """
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-emerald-500 outline-none transition-all duration-300'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-emerald-500 outline-none transition-all duration-300'})
    )
    email = forms.EmailField(
        max_length=254, 
        required=True,
        widget=forms.EmailInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-emerald-500 outline-none transition-all duration-300'})
    )
    phone_number = forms.CharField(
        max_length=20, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-emerald-500 outline-none transition-all duration-300'})
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-emerald-500 outline-none transition-all duration-300'
        })
    )
    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'hidden'})
    )
    
    # Agreement to terms and conditions
    agreement = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'w-5 h-5 text-emerald-500 border-2 border-gray-300 rounded-lg focus:ring-emerald-500'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-emerald-500 outline-none transition-all duration-300'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update password widgets
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-emerald-500 outline-none transition-all duration-300'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-emerald-500 outline-none transition-all duration-300'})
        
        # Add help texts in Arabic
        self.fields['username'].help_text = _('مطلوب. 150 حرفًا أو أقل. يمكن أن تحتوي على أحرف وأرقام و@ / . / + / - / _ فقط.')
        self.fields['password1'].help_text = _('• يجب أن تحتوي كلمة المرور على 8 أحرف على الأقل.<br>• يجب ألا تكون كلمة المرور شائعة جدًا.<br>• يجب ألا تكون كلمة المرور مكونة من أرقام فقط.')
        self.fields['password2'].help_text = _('أدخل نفس كلمة المرور مرة أخرى للتحقق.')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('هذا البريد الإلكتروني مستخدم بالفعل.'))
        return email


class TourGuideProfileForm(forms.ModelForm):
    """
    Form for tour guide profile updates.
    """
    first_name = forms.CharField(
        max_length=30, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus'})
    )
    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'hidden'})
    )
    banner_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'hidden'})
    )
    
    class Meta:
        model = TourGuide
        fields = (
            'bio', 'phone_number', 'years_of_experience',
            'languages', 'certifications', 'specialties',
            'website', 'twitter', 'instagram', 'facebook', 'linkedin', 'youtube'
        )
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus resize-none'
            }),
            'phone_number': forms.TextInput(attrs={'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus'}),
            'years_of_experience': forms.NumberInput(attrs={'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus'}),
            'languages': forms.SelectMultiple(attrs={'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus'}),
            'certifications': forms.SelectMultiple(attrs={'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus'}),
            'specialties': forms.SelectMultiple(attrs={'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus'}),
            'website': forms.URLInput(attrs={'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus'}),
            'twitter': forms.URLInput(attrs={'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus', 'placeholder': 'رابط تويتر'}),
            'instagram': forms.URLInput(attrs={'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus', 'placeholder': 'رابط انستجرام'}),
            'facebook': forms.URLInput(attrs={'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus', 'placeholder': 'رابط فيسبوك'}),
            'linkedin': forms.URLInput(attrs={'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus', 'placeholder': 'رابط لينكد إن'}),
            'youtube': forms.URLInput(attrs={'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus', 'placeholder': 'رابط يوتيوب'}),
        }
        labels = {
            'bio': _('نبذة تعريفية'),
            'phone_number': _('رقم الجوال'),
            'years_of_experience': _('سنوات الخبرة'),
            'languages': _('اللغات'),
            'certifications': _('الشهادات'),
            'specialties': _('التخصصات'),
            'website': _('الموقع الإلكتروني'),
            'twitter': _('تويتر'),
            'instagram': _('انستجرام'),
            'facebook': _('فيسبوك'),
            'linkedin': _('لينكد إن'),
            'youtube': _('يوتيوب'),
        }


class TourPackageForm(forms.ModelForm):
    """
    Form for adding or editing tour packages.
    """
    class Meta:
        model = TourPackage
        fields = (
            'title', 'description', 'duration', 'price', 'discount_price', 
            'included_services', 'excluded_services', 'max_people', 'locations', 
            'is_active', 'is_featured'
        )
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus'}),
            'description': forms.Textarea(attrs={
                'rows': 5,
                'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus resize-none'
            }),
            'duration': forms.TextInput(attrs={'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus'}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus'}),
            'discount_price': forms.NumberInput(attrs={'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus'}),
            'included_services': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus resize-none'
            }),
            'excluded_services': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus resize-none'
            }),
            'max_people': forms.NumberInput(attrs={'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus'}),
            'locations': forms.SelectMultiple(attrs={'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-5 h-5 text-emerald-500 border-2 border-gray-300 rounded-lg focus:ring-emerald-500'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'w-5 h-5 text-emerald-500 border-2 border-gray-300 rounded-lg focus:ring-emerald-500'}),
        }
        labels = {
            'title': _('عنوان الباقة'),
            'description': _('وصف الباقة'),
            'duration': _('المدة'),
            'price': _('السعر'),
            'discount_price': _('سعر مخفض (اختياري)'),
            'included_services': _('الخدمات المشمولة'),
            'excluded_services': _('الخدمات غير المشمولة'),
            'max_people': _('الحد الأقصى للأشخاص'),
            'locations': _('المواقع'),
            'is_active': _('نشط'),
            'is_featured': _('مميز'),
        }


class GalleryForm(forms.ModelForm):
    """
    Form for adding gallery images.
    """
    uploaded_image = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={'class': 'hidden', 'id': 'image-upload'}),
        help_text=_('اختر صورة لإضافتها إلى معرض الصور')
    )
    
    class Meta:
        model = Gallery
        fields = ('title', 'description', 'order')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus'}),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus resize-none'
            }),
            'order': forms.NumberInput(attrs={'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus'}),
        }
        labels = {
            'title': _('عنوان الصورة'),
            'description': _('وصف الصورة'),
            'order': _('الترتيب'),
        }


class VideoForm(forms.ModelForm):
    """
    Form for adding videos.
    """
    class Meta:
        model = Video
        fields = ('title', 'youtube_url', 'description', 'order')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus'}),
            'youtube_url': forms.URLInput(attrs={'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus'}),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus resize-none'
            }),
            'order': forms.NumberInput(attrs={'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus'}),
        }
        labels = {
            'title': _('عنوان الفيديو'),
            'youtube_url': _('رابط الفيديو على يوتيوب'),
            'description': _('وصف الفيديو'),
            'order': _('الترتيب'),
        }


class WorkScheduleForm(forms.ModelForm):
    """
    Form for adding work schedules.
    """
    class Meta:
        model = WorkSchedule
        fields = ('location', 'start_date', 'end_date', 'notes')
        widgets = {
            'location': forms.Select(attrs={'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus appearance-none bg-white'}),
            'start_date': forms.DateInput(attrs={
                'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-5 py-4 rounded-xl border border-gray-200 input-focus resize-none'
            }),
        }
        labels = {
            'location': _('الموقع'),
            'start_date': _('تاريخ البداية'),
            'end_date': _('تاريخ النهاية'),
            'notes': _('ملاحظات'),
        } 