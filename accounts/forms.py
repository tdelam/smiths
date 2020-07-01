from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    
    class Meta:
        model = UserProfile
        exclude = ('user', 'is_active', 'is_corporate_account')
    
class RegistrationForm(UserCreationForm):
    username = forms.RegexField(label="Username", max_length=30, regex=r'^[\w.@+-]+$')
    password1 = forms.CharField(label="Password",
        widget=forms.PasswordInput)
    password2 = forms.CharField(label="Re-Password",
        widget=forms.PasswordInput)
    email = forms.EmailField(label="Email Address", max_length="50")