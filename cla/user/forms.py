from django import forms
from .models import ProfilePhoto
    
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = ProfilePhoto
        fields = ['profile_picture']