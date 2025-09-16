from rest_framework import serializers
from order.models import Cart, CartItem
from product.serializers import ProductSerializer
from product.models import Product
from .models import Order, OrderItem
from .services import OrderService

class SimplProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price']

class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    class Meta:
        model = CartItem
        fields = ['id','product_id', 'quantity']

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            self.instance = cart_item.save()

        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
        
        return self.instance
    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                f"product with id {value} does not exists"
            )
        return value

class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

class CartItemSerializer(serializers.ModelSerializer):
    # product_price = serializers.SerializerMethodField(method_name='get_product_price')
    # product = ProductSerializer()
    product = SimplProductSerializer()
    total_price = serializers.SerializerMethodField(method_name='get_total_price')
    class Meta:
        model = CartItem
        fields = ['id','product','quantity','total_price']
    # def get_product_price(self, cart_item):
        # return cart_item.product.price
    def get_total_price(self, cart_item:CartItem):
        return cart_item.quantity * cart_item.product.price

class CartSerializer(serializers.ModelSerializer):
    grand_total_price = serializers.SerializerMethodField(method_name='get_grand_total_price')
    items = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = ['id','user','items','grand_total_price']
        read_only_fields = ['user']
    
    def get_grand_total_price(self, cart:Cart):
        #উপরে cart:Cart হলো cart=variable এবং Cart হলো Modelname
        #list compression এর মাধ্যমে grand total price বের করা হয়েছে।
        #এখানে cart থেকে related name 'items' এর মাধ্যমে সকল CartItems কে query করা হয়েছে।
        # এরপর সেখান থেকে for loop ব্যবহার করে প্রত্যেকটা cart item এর price and quantity গুনন করে sum করা হয়েছে।
        return sum([item.product.price * item.quantity for item in cart.items.all()])

class EmptySerializer(serializers.Serializer):
    pass

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError('No cart found fith This id')
        if not CartItem.objects.filter(cart_id=cart_id).exists():
            raise serializers.ValidationError('Cart is empty')
        return cart_id
    
    def create(self, validated_data):
        user_id = self.context['user_id']
        cart_id = validated_data['cart_id']
        try:
            order = OrderService.create_order(user_id=user_id, cart_id=cart_id)
            return order
        except ValueError as e:
            raise serializers.ValidationError(str(e))

    def to_representation(self, instance):
        return OrderSerializer(instance).data


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimplProductSerializer()
    class Meta:
        model = OrderItem
        fields = ['id', 'product','quantity','price','total_price']

class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

"""
# এই কোডটি দরকার নাই। কারণ আমরা OrderViewSet এ action হিসেবে cancel ব্যবহার করবো।
    def update(self, instance, validated_data):
        user = self.context['user']
        new_status = validated_data['status']

        if new_status == Order.CANCELED:
            return OrderService.cancel_order(order=instance, user=user)

        # Admin কি না
        if not user.is_staff:
            raise serializers.ValidationError({'details': 'You are not allowed to update this order'})
        
        # Admin যদি হয়। তাহলে এইভাবে করা যায়।
        # instance.status = new_status
        # instance.save()
        # return instance
        # এছাড়া সরাসরি ModelSerializer এর update মেথডকে ব্যবহার করেও করা যায়।
        return super().update(instance, validated_data)
"""

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = ['id','user','status','total_price','created_at','items']