from django.test import TestCase
from django.contrib.auth.models import User
from user.models import UserProfile

class UserProfileTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", email="test@example.com")
    
    def test_user_profile_creation(self):
        profile = UserProfile.objects.create(user=self.user)
        self.assertEqual(profile.user.username, "testuser")
        self.assertEqual(profile.role, "patron")
