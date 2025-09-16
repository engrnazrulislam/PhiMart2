from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from product.models import Product, Category, Review, ProductImage
from rest_framework import status
from product.serializers import ProductSerializer, CategorySerializer, ReviewSerializer, ProductImageSerializer
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from product.filters import ProductFilter
from rest_framework.filters import SearchFilter
from rest_framework.filters import OrderingFilter
# from rest_framework.pagination import PageNumberPagination
from product.paginations import DefaultPagination
# from rest_framework.permissions import IsAdminUser, AllowAny
from api.permission import IsAdminOrReadOnly, FullDjangoModelPermission
from rest_framework.permissions import DjangoModelPermissions, DjangoModelPermissionsOrAnonReadOnly
from product.permissions import IsReviewAuthorOrReadOnly
from drf_yasg.utils import swagger_auto_schema

#এখন আমরা নতুন কিছু শিখবো যা ব্যবহার করলে আমাদের কোড অনেক কমে যাবে।
class ProductViewSet(ModelViewSet):
    """
    Product API End Point is used for product related task
    - Authorized user can view the product
    - Admin User can change, update, delete product etc.
    """
    #এখানে আমরা select_related field ব্যবহার করেছিল কারন। তখন আমাদের Category সমুহকে Nested আকারে দেখানোর জন্য। কিন্তু এখন আমরা শুধুমাত্র id দেখাইতেছি তাই select_related field দারকার নেই।
    # queryset = Product.objects.select_related('category').all()
    # queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # DjangoFilterBackend ব্যবহার করে product filtering করা।
    # queryset = Product.objects.all() # এর পরিবর্তে আমরা method ব্যবহার করেছি।
    #জ্যাংগু ফিল্টার ব্যবহার করে ফিল্টারিং করা
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = ['category_id','price']
    
    # আগে filterset_fields ব্যবহার করা হতো। এখন এখানে আমরা Django FilterSet ব্যবহার করবো।
    filterset_class = ProductFilter
    # pagination_class = PageNumberPagination
    pagination_class = DefaultPagination
    search_fields = ['name', 'description','category__name']
    ordering_fields = ['price','updated_at']
    # কারা কারা product দেখতে পারবে এবং কারা কারা product add করতে পারবে।
    # permission_classes = [IsAdminUser]
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Product.objects.prefetch_related('images').all()

    @swagger_auto_schema(
        operation_summary="Retrive a lists of products"
    )
    def list(self, request, *args, **kwargs):
        """Only Authorized User Can View The Product"""
        return super().list(request, *args, **kwargs)
    @swagger_auto_schema(
            operation_summary="Create a product by admin",
            operation_description="This is allow an admin to create a product",
            request_body=ProductSerializer,
            responses={
                201: ProductSerializer,
                400: 'Bad Request'
            }
    )
    def create(self, request, *args, **kwargs):
        """Only Admin User Can Create, Delete, Update the Product"""
        return super().create(request, *args, **kwargs)
    # permission_classes = [DjangoModelPermissions]
    # permission_classes = [FullDjangoModelPermission]
    # permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    # def get_permissions(self):
    #     if self.request.method == 'GET':
    #         return [AllowAny()] # শুধু product দেখতে পারবে।
    #     return [IsAdminUser()] # product add, delete করতে পারবে।
    
    # যদি আমরা ক্যাটাগরি আইডি দ্বারা প্রোডাক্ট সার্চ করার কোডঃ
    # এটি একটি ম্যানুয়াল পদ্ধতি। 
    # def get_queryset(self):
    #     queryset = Product.objects.all()
    #     category_id = self.request.query_params.get('category_id')
    #     if category_id is not None:
    #         queryset = Product.objects.filter(category_id=category_id)
    #     return queryset
    
    # এখানে delete মেথডে পরিবর্তে destroy মেথড ব্যবহার করা হয়েছে। কারন ModelViewSet এর মধ্যে এটি ব্যবহার করা হয়েছে।
    # def destroy(self, request, *args, **kwargs):
    #     product = self.get_object()
    #     if product.stock > 10:
    #         return Response({'message': 'Product with stock more then 10 could not be deleted'})
    #     self.perform_destroy(product)
    #     return Response(status=status.HTTP_204_NO_CONTENT)

class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminOrReadOnly]
    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs.get('product_pk'))
    def perform_create(self, serializer):
        serializer.save(product_id=self.kwargs.get('product_pk'))

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.annotate(product_count=Count('products')).all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        category = self.get_object()
        if category.product_count >= 0:
            return Response({'message': 'You have more than 10 product'})
        self.destroy(category)
        return Response(status=status.HTTP_204_NO_CONTENT)
        
#
@api_view(['GET','POST'])
def view_products(request):
    if request.method == 'GET':
        products = Product.objects.select_related('category').all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        # serializer = ProductSerializer(data=request.data, context={'request': request}) # এই (data=request.data) কে deserializer বলে
        serializer = ProductSerializer(data=request.data) # এই (data=request.data) কে deserializer বলে
        # if serializer.is_valid():
        #     print(serializer.validated_data)
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # else:
        #     return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        #এর পরিবর্তে আমরা এক লাইনেও এটি ব্যবহার করতে পারি। নিচের মত করে।
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
"""
class ViewProducts(APIView):
    def get(self, request):
        products = Product.objects.select_related('category').all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
"""
class ViewProducts(ListCreateAPIView):
    # Attributes সমুহ ব্যবহার করা হয় যদি কোন Conditional QuersySet ব্যবহার করা না হয়।
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer

    # মেথড Overriding শুধুমাত্র কন্ডিশনাল queryset কে পাঠানোর জন্য ব্যবহার করা হয়।
    #  def get_queryset(self):
    #      return Product.objects.select_related('category').all()
    #  def get_serializer_class(self):
    #      return ProductSerializer
    #  def get_serializer_context(self):
    #      return {'request': self.request}



@api_view(['GET', 'PUT', 'DELETE'])
def view_specific_product(request, id):
    # try:
    #     product = Product.objects.get(pk=id)
    #     product_dict = {'id': product.id, 'name': product.name, 'price': product.price}
    #     return Response(product_dict)
    # except Product.DoesNotExist:
    #     return Response({'message': 'Product does not exists'}, status=status.HTTP_404_NOT_FOUND)
    
    # try-except এর পরিবর্তে আমাদের নিচের get_object_or_404 মেথব ব্যবহার করে সহজেই কাজটি করতে পারি।
    # if request.method == 'GET':
    # product = get_object_or_404(Product, pk=pk)
    # product_dict = {'id': product.id, 'name': product.name, 'price': product.price}
    #এর পরিবর্তে আমরা product serializer কে ব্যবহার করবো।
    # serializer = ProductSerializer(product)
    # return Response(serializer.data)
    
    # এটি সাধারণত Specific Product এর মধ্যে করা হয় না। এটি অনেকগুলো product এর মধ্যে করা হয়।
    # if request.method == 'POST':
    #     serializer = ProductSerializer(data=request.data) # এই (data=request.data) কে deserializer বলে
    #     if serializer.is_valid():
    #         print(serializer.validated_data)
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     else:
    #         return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    if request.method == 'GET':
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    if request.method == 'PUT':
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    if request.method == 'DELETE':
        product = get_object_or_404(Product, pk=id)
        copy_of_product = product # কি delete হবে তা কপি রাখতে।
        product.delete()
        serializer = ProductSerializer(copy_of_product)# যদি কি Delete হয়েছে তা দেখাতে চাই
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
"""
class ViewSpecificProduct(APIView):
    def get(self, request, id):
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    def put(self, request, id):
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    def delete(self, request, id):
        product = get_object_or_404(Product, pk=id)
        copy_of_product = product # কি delete হবে তা কপি রাখতে।
        product.delete()
        serializer = ProductSerializer(copy_of_product)# যদি কি Delete হয়েছে তা দেখাতে চাই
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
"""
class ViewSpecificProduct(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'

    def delete(self, request, id, *args, **kwargs):
        product = get_object_or_404(Product, pk=id)
        if product.stock > 10:
            return Response({'message': 'Product with stock more then 10 could not be deleted'})
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
@api_view()
def view_category(request):
    # category = Category.objects.all()
    category = Category.objects.annotate(product_count=Count('products')).all()
    serializer = CategorySerializer(category, many=True)
    return Response(serializer.data)

"""
class ViewCategory(APIView):
    def get(self, request):
        category = Category.objects.annotate(product_count=Count('products')).all()
        serializer = CategorySerializer(category, many=True)
        return Response(serializer.data)
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
"""
class ViewCategory(ListCreateAPIView):
    queryset = Category.objects.annotate(product_count=Count('products')).all()
    serializer_class = CategorySerializer



@api_view()
def view_specific_category(request, id):
    category = get_object_or_404(Category, pk=id)
    serializer = CategorySerializer(category)
    return Response(serializer.data)
"""
class ViewSpecificCategory(APIView):
    def get(self, request, id):
        category = get_object_or_404(
            Category.objects.annotate(product_count=Count('products')).all(), 
            pk=id)
        serializer = CategorySerializer(category)
        return Response(serializer.data)
    def put(self, request, id):
        category = get_object_or_404(
            Category.objects.annotate(product_count=Count('products')).all(),
            pk=id)
        serializer = ProductSerializer(category, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    def delete(self, request, id):
        category = get_object_or_404(
            Category.objects.annotate(product_count=Count('products')).all(),
            pk=id)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
"""
class ViewSpecificCategory(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.annotate(product_count=Count('products')).all()
    serializer_class = CategorySerializer
    lookup_field = 'id'

    def delete(self, request, id):
        category = get_object_or_404(
            Category.objects.annotate(product_count=Count('products')).all(),
            pk=id)
        if category.product_count >= 0:
            return Response({'message': 'You have more than 10 product'})
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# For nested router
class ReviewViewSet(ModelViewSet):
    # queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs.get('product_pk'))

    def get_serializer_context(self):
        return {'product_id': self.kwargs.get('product_pk')}