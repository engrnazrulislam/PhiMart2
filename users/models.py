from django.db import models
from django.contrib.auth.models import AbstractUser # এই মডেলটি Import করা হয়েছে।
from users.managers import CustomUserManager
# Create your models here.
class User(AbstractUser):
    username = None # এখানে মডেলের মধ্যে username field কে Override করা হয়েছে।
    email = models.EmailField(unique=True) # এখানে মডেলের মধ্যে email field কে Override করা হয়েছে।
    address = models.TextField(blank=True, null=True) # Add extra fields like address
    phone_number = models.CharField(max_length=15, blank=True, null=True) # Add extra fields like phone_number

    USERNAME_FIELD = 'email' # যেহেতু username field এর পরিবর্তে email field কে লগিনের জন্য ব্যবহার করা হবে তাই এটিকে চিনিয়ে দেয়া।
    REQUIRED_FIELDS = [] # যেহেতু superuser তৈরি করার সময় username field কে required field হিসেবে বিবেচনা করা হতো তাই এটিকে ফাকা রাখা
    
    # এখানে ইউজারটি হবে CustomUserManager
    objects = CustomUserManager()

    def __str__(self):
        return self.email

