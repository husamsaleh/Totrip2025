from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class UserRegistrationForm(UserCreationForm):
    """
    Form for user registration
    """
    first_name = forms.CharField(max_length=30, required=True, 
                                 widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-emerald-500 outline-none transition-all duration-300'}))
    last_name = forms.CharField(max_length=30, required=True,
                               widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-emerald-500 outline-none transition-all duration-300'}))
    username = forms.CharField(max_length=150, required=True,
                              widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-emerald-500 outline-none transition-all duration-300'}))
    email = forms.EmailField(required=True,
                            widget=forms.EmailInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-emerald-500 outline-none transition-all duration-300'}))
    password1 = forms.CharField(required=True,
                               widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-emerald-500 outline-none transition-all duration-300'}))
    password2 = forms.CharField(required=True,
                               widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-emerald-500 outline-none transition-all duration-300'}))
    phone_number = forms.CharField(max_length=20, required=False,
                                  widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-emerald-500 outline-none transition-all duration-300'}))
    agreement = forms.BooleanField(required=True,
                                  widget=forms.CheckboxInput(attrs={'class': 'w-5 h-5 text-emerald-500 border-2 border-gray-300 rounded-lg focus:ring-emerald-500'}))
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # UserProfile will be created automatically via signal
            if hasattr(user, 'user_profile'):
                user.user_profile.phone_number = self.cleaned_data['phone_number']
                user.user_profile.save()
        
        return user

class UserProfileForm(forms.ModelForm):
    """
    Form for editing user profile
    """
    first_name = forms.CharField(max_length=30, required=True,
                                widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-emerald-500 outline-none transition-all duration-300'}))
    last_name = forms.CharField(max_length=30, required=True,
                               widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-emerald-500 outline-none transition-all duration-300'}))
    email = forms.EmailField(required=True,
                            widget=forms.EmailInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-emerald-500 outline-none transition-all duration-300'}))
    bio = forms.CharField(required=False,
                         widget=forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-emerald-500 outline-none transition-all duration-300'}))
    phone_number = forms.CharField(max_length=20, required=False,
                                  widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-emerald-500 outline-none transition-all duration-300'}))
    
    class Meta:
        model = UserProfile
        fields = ('bio', 'phone_number')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize User fields if we have an instance
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email 