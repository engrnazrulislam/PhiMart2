from django.contrib.auth.base_user import BaseUserManager

class CustomUserManager(BaseUserManager):
    # CustomUserManager তৈরি করার জন্য ২টি মেথডকে Override করতে হবে।
    # সাধারন user এর জন্য
    def create_user(self, email, password = None, **extra_fields):
        if not email:
            raise ValueError('This email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db) # ডাটাবেজে স্টোর করার জন্য 
        return user
    

    # superuser এর জন্য
    def create_superuser(self, email, password = None, **extra_fields):
        #সুপার ইউজারে এই ২টি ফিল্ড থাকে।
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True')
        
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True')
        
        # এখানে আমরা create_user মেথড কে কল করে email, password, extra_fields কে পাস করেছি।
        return self.create_user(email, password, **extra_fields)
