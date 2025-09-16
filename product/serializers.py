from rest_framework import serializers
from decimal import Decimal
from product.models import Category, Product, Review, ProductImage
from django.contrib.auth import get_user_model
User = get_user_model()

# class CategorySerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     name = serializers.CharField()
#     description = serializers.CharField()

# class ProductSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     name = serializers.CharField()
#     unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, source='price')

#     price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')

#     # category = serializers.PrimaryKeyRelatedField(
#     #     queryset = Category.objects.all()
#     # )
#     # category = serializers.StringRelatedField()
#     # category = CategorySerializer()
#     category = serializers.HyperlinkedRelatedField(
#         queryset = Category.objects.all(),
#         view_name = 'view-specific-category'
#     )

#     def calculate_tax(self, product):
#         return round((product.price * Decimal(1.1)), 2)

# ProductImageSerializer for ProductImage Model
class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    class Meta:
        model = ProductImage
        fields = ['id','image']

# Model Serializer
class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        # fields = '__all__' # এই ভাবে সকল ফিল্ড না দেখানোই ভাল
        fields = ['id', 'name','description', 'price', 'stock','category', 'price_with_tax', 'images']

    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')

    # category = serializers.HyperlinkedRelatedField(
    #     queryset = Category.objects.all(),
    #     view_name = 'view-specific-category'
    # )

    def calculate_tax(self, product):
        return round((product.price * Decimal(1.1)), 2)
    
    # field level validation
    def validate_price(self,price):
        if price < 0:
            raise serializers.ValidationError('Price could not be negative')
        return price

    #যদি product object এর মধ্যে অন্য কোন field কে add করতে চাই তবে create মেথডকে Override নিম্নভাবে করতে হয়।
    # def create(self, validated_data):
    #     product = Product(**validated_data) # পূর্বের সকল ফিল্ড নিয়ে একটি অবজেক্ট তৈরি হয়।
    #     product.other = 1 # এই ফিল্ডটি অবজেক্টে যুক্ত হবে।
    #     product.save() # এখানে অবজেক্টটি সেভ হবে। বা create হবে।
    #     return product

    

    # Object level validation. এটি এই কন্টেক্সট এর জন্য প্রযোজ্য নয়। তারপরও আমরা দেখালাম
    # def validate(self, attrs):
    #     if attrs['password1'] != attrs['password2']:
    #         raise serializers.ValidationError("finish must occur after start")
    #     return attrs



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description','product_count']

    product_count = serializers.IntegerField(read_only=True, help_text="Return the number of product in this category") # read_only=True দ্বারা বুঝায় এটি শুধুমাত্র গেট করার সময় কাজ করবে কিন্তু post এর সময় কাজ করবে না।
        
    # product_count = serializers.SerializerMethodField(
    #     method_name = 'get_product_count'
    # )

    # def get_product_count(self, category):
    #     count = Product.objects.filter(category=category).count()
    #     return count
# DRF Nested Router এর জন্য serializer

class SimpleUserSerializer(serializers.ModelSerializer):
    name  = serializers.SerializerMethodField(method_name='get_current_user_name')
    class Meta:
        model = User
        fields = ['id','name']
        
    def get_current_user_name(self, obj):
        return obj.get_full_name()

class ReviewSerializer(serializers.ModelSerializer):
    # user = SimpleUserSerializer()
    user = serializers.SerializerMethodField(method_name='get_user')

    class Meta:
        model = Review
        # fields = ['id', 'name', 'description', 'product']
        fields = ['id', 'user','product','ratings','comment']
        read_only_fields = ['user','product']

    def get_user(self, obj):
            return SimpleUserSerializer(obj.user).data

    def create(self, validated_data):
        product_id = self.context['product_id']
        review = Review.objects.create(product_id=product_id, **validated_data)
        return review

