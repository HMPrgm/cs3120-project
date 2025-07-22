# textbook/models.py
from django.db import models
from django.utils.timezone import now
from user.models import User, get_role
from django.contrib.auth.models import User
from django.db.models import Avg

class Class(models.Model):
    DEPARTMENT_CHOICES = [
        ('CS', 'Computer Science'),
        ('MATH', 'Mathematics'),
        ('PHYS', 'Physics'),
        ('PHIL', 'Philosophy'),
        ('APMA', 'Applied Math'),
        ('GERM', 'German'),
        ('ECE', 'Electrical and Computer Engineering'),
        # Add more departments as needed
    ]

    department = models.CharField(max_length=10, choices=DEPARTMENT_CHOICES)
    number = models.CharField(max_length=10)  # Using CharField for numbers like "101A"
    name = models.CharField(max_length=200)
    id = models.AutoField(primary_key=True)

    def __str__(self):
        return f"{self.department} {self.number}"

    class Meta:
        verbose_name_plural = "Classes"

class Textbook(models.Model):
    CONDITION_CHOICES = [
        ('NEW', 'New'),
        ('GOOD', 'Good'),
        ('FAIR', 'Fair'),
        ('POOR', 'Poor'),
    ]

    id = models.AutoField(primary_key=True)
    associated_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='textbooks')
    published_date = models.DateField()
    added_date = models.DateTimeField(default=now)
    condition = models.CharField(max_length=4, choices=CONDITION_CHOICES)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
    checked_out = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    library = models.ForeignKey('Library', on_delete=models.SET_NULL, null=True, blank=True, related_name='textbooks')

    def __str__(self):
        return f"{self.title} by {self.author}"
    
    @property
    def average_rating(self):
        avg = self.ratings.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0
    
    def rating_count(self):
        return self.ratings.count()
    
    def get_picture(self):
        picture = TextbookPhoto.objects.filter(textbook=self).first()
        if (picture):
            return picture
        return None
    
class TextbookRating(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    textbook = models.ForeignKey(Textbook, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='textbook_ratings')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.textbook.title} rating by {self.user.username} - {self.rating} stars"
        
class TextbookRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('DENIED', 'Denied'),
    ]

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='textbook_requests')
    textbook = models.ForeignKey(Textbook, on_delete=models.CASCADE, related_name='requests')
    request_date = models.DateTimeField(default=now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"Request by {self.user.username} for '{self.textbook.title}' - Status: {self.status}"
    
    

class TextbookPhoto(models.Model):
    textbook = models.OneToOneField(Textbook, on_delete = models.CASCADE, related_name = "textbook", null = True, blank = True)
    picture = models.ImageField(upload_to='textbook_pictures/', blank=True, null=True)

    
class Collection(models.Model):
    id = models.AutoField(primary_key=True)
    textbooks = models.ManyToManyField(Textbook)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collection')
    private = models.BooleanField(default=False)
    allowed_patrons = models.ManyToManyField(User, blank=True, related_name="allowed_collection")
    
    @property
    def count(self):
        return self.textbooks.count()

    def add_patron(self, user_to_add):
        if user_to_add and isinstance(user_to_add, User):
            self.allowed_patrons.add(user_to_add)

    def remove_patron(self, user_to_remove):
        if user_to_remove and isinstance(user_to_remove, User):
            self.allowed_patrons.remove(user_to_remove)

    def is_patron_allowed(self, user_to_check):
        if not user_to_check or not isinstance(user_to_check, User) or not user_to_check.is_authenticated:
            return False
        return self.allowed_patrons.filter(pk=user_to_check.pk).exists()
    
    def get_collections_by_user(user, query = ""):
        if not user or not user.is_authenticated:
            return Collection.objects.filter(private=False)

        if query != "":
            return Collection.objects.filter(
                models.Q(title__icontains=query, private=False) |  # Condition 1: Collection is public
                models.Q(title__icontains=query, user=user)
            ).distinct()
        else:
            return Collection.objects.filter(
                models.Q(private=False) |  # Condition 1: Collection is public
                models.Q(user=user)
            ).distinct()
        
    def get_private_collections(query = ""):
        if query != "":
            return Collection.objects.filter(
                title__icontains=query,
                private=True
            )
        else:
            return Collection.objects.filter(
                private=True
            )
    def __str__(self):
        return f"{self.name}, created by {self.user}"


    
class CollectionRequests(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('DENIED', 'Denied'),
    ]


    id = models.AutoField(primary_key=True)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    request_date = models.DateTimeField(default=now)

    
class Library(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='libraries')
    collections = models.ManyToManyField(Collection, blank=True, related_name='libraries')
    tags = models.CharField(max_length=300, blank=True) 
    public = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (by {self.user.username})"

    @property
    def count(self):
        return self.collections.count()

    def tag_list(self):
        return [tag.strip().lower() for tag in self.tags.split(',') if tag.strip()]