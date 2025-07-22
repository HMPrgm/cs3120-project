from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

from allauth.account.signals import user_signed_up
from django.dispatch import receiver



class UserProfile(models.Model):

    USER_TYPES = [
        ('anonymous', 'Anonymous'),
        ('patron', 'Patron'),
        ('librarian', 'Librarian'),
    ]

    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name = "profile", null = True, blank = True)
    role = models.CharField(max_length = 20, choices = USER_TYPES, default = 'patron')
    joined_cla_date = models.DateTimeField(default = now)
    

    def __str__(self):
        return f"{self.user.username if self.user else 'Anonymous'} - {self.get_role_display()}"

    def get_profile_picture(self):
        profile_picture = ProfilePhoto.objects.filter(user_profile=self).first()
        if (profile_picture):
            return profile_picture.profile_picture
    
        return None


class ProfilePhoto(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete = models.CASCADE, related_name = "user_profile", null = True, blank = True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

@receiver(user_signed_up)
def user_signed_up_handler(request, user, **kwargs):
    # Your custom code here
    # For example:
    print("Creating user profile for", user.username)  # Debug print
    UserProfile.objects.create(
        user=user,
        role='patron'  # or whatever default role you want
    )
    
def get_role(user):
    if user is None:
        return "anonymous"
    elif not hasattr(user, 'profile') or user.profile is None:
        return "anonymous"  # or some other default role
    else:
        return 'librarian' if user.profile.role == 'librarian' else 'patron'
    