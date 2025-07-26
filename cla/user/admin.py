from django.contrib import admin

# Register your models here.
from .models import UserProfile, ProfilePhoto

admin.site.register(UserProfile)
admin.site.register(ProfilePhoto)