from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from product.validators import validate_file_size
from cloudinary.models import CloudinaryField

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    # image = models.ImageField(
    #     upload_to="products/images/", blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id',]

    def __str__(self):
        return self.name

# Model for Product Image
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    # image = models.ImageField(upload_to="products/images/", validators=[validate_file_size]) # Due to required field, do not use blank=true, null=true
    image = CloudinaryField('image') # ('image') দ্বারা বুঝায় আমরা কোন নামে image রাখবো।
    #কি ভাবে file নিয়ে কাজ করতে হয়। এখানে তা দেখানো হলো। আমাদের প্রজেক্টে only image নিয়ে কাজ হবে
    #তাই এট আমরা কমেন্ট করে দিলাম।
    # file = models.FileField(upload_to="product/files", validators=FileExtensionValidator(['pdf']))

# Model for build API    
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ratings = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Reviewed by {self.user.first_name} {self.user.last_name} on {self.product.name}'

# Step to build an API
# ১। Model কে রেডি রাখতে হবে
# ২। serializer বানাইতে হবে
# ৩। ViewSet রেডি করতে হবে
# ৪। router টিকে রেডি করতে হবে।
# এই চারটি স্টেপ আমাদেরকে ফলো করতে হয় আমাদের যে কোন api কে বানানোর জন্য

"""
<Product: laptop> এর properties গুলো যেমনঃ id, name ইত্যাদি।
এগুলো আমরা যে ভাবে একসেস করবোঃ
product_id
product_name
এই product গুলো কি দিয়ে খুজবে তার জন্য lookup field এর আমরা product
লিখে দিয়েছি।

"""
    
