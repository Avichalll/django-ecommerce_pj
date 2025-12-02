from rest_framework import serializers
from django.db.models import Avg
from apps.products.models import Product, ProductImage, Category, Review
from .product_image import ProductImageSerializer, ProductImageCreateSerializer
from .category import CategoryListSerializer
from .review import ReviewSerializer


class ProductListSerializer(serializers.ModelSerializer):
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'price',
            'discount_price',
            'current_price',
            'category_name',
            'primary_image',
            'stock_status',
            'is_active'
        ]
    
    def get_primary_image(self, obj):
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            return ProductImageSerializer(primary).data
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    
    category = CategoryListSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'sku',
            'description',
            'short_description',
            'price',
            'discount_price',
            'current_price',
            'quantity',
            'stock_status',
            'category',
            'brand',
            'weight',
            'dimensions',
            'is_active',
            'is_featured',
            'images',
            'reviews',
            'average_rating',
            'review_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(reviews.aggregate(Avg('rating'))['rating__avg'], 1)
        return None
    
    def get_review_count(self, obj):
        return obj.reviews.filter(is_approved=True).count()


class ProductCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating products with nested images.
    MUST implement create() method for nested writable fields.
    """
    
    images = ProductImageCreateSerializer(many=True, required=False)
    
    class Meta:
        model = Product
        fields = [
            'name',
            'slug',
            'sku',
            'description',
            'short_description',
            'price',
            'discount_price',
            'quantity',
            'stock_status',
            'category',
            'brand',
            'weight',
            'dimensions',
            'is_active',
            'is_featured',
            'images'
        ]

    def validate_category(self, value):
        """Validate category exists and is active"""
        if not value.is_active:
            raise serializers.ValidationError("This category is inactive.")
        return value
    
    def validate_price(self, value):
        """Validate price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value
    
    def validate_images(self, value):
        """Validate images list"""
        if value and len(value) > 10:
            raise serializers.ValidationError("Maximum 10 images allowed.")
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        price = attrs.get('price')
        discount_price = attrs.get('discount_price')
        
        if discount_price and price and discount_price >= price:
            raise serializers.ValidationError({
                'discount_price': 'Discount price must be less than regular price.'
            })
        
        return attrs
    
    def create(self, validated_data):
        """
        Custom create method to handle nested images.
        This is REQUIRED for writable nested serializers.
        """
        # Extract images from validated data
        images_data = validated_data.pop('images', [])
        
        # Create the product
        product = Product.objects.create(**validated_data)
        
        # Create images linked to product
        for index, image_data in enumerate(images_data):
            # Set order if not provided
            if 'order' not in image_data or image_data.get('order') is None:
                image_data['order'] = index
            
            # Set first image as primary if none specified
            if index == 0 and not any(img.get('is_primary', False) for img in images_data):
                image_data['is_primary'] = True
            
            ProductImage.objects.create(product=product, **image_data)
        
        return product


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating products"""
    
    class Meta:
        model = Product
        fields = [
            'name',
            'slug',
            'sku',
            'description',
            'short_description',
            'price',
            'discount_price',
            'quantity',
            'stock_status',
            'category',
            'brand',
            'weight',
            'dimensions',
            'is_active',
            'is_featured'
        ]
    
    def validate_category(self, value):
        if value and not value.is_active:
            raise serializers.ValidationError("This category is inactive.")
        return value