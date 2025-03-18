from rest_framework import serializers
from .models import Category, Product
from stores.serializers import StoreSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug', 'created_at']
        read_only_fields = ['id', 'created_at']

class ProductSerializer(serializers.ModelSerializer):
    store = StoreSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'store', 'category', 'name', 'description', 'price', 'stock', 'image', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'price', 'stock', 'image', 'is_active']
        
    def create(self, validated_data):
        user = self.context['request'].user
        if not hasattr(user, 'store'):
            raise serializers.ValidationError("You must have a store to create products.")
        
        product = Product.objects.create(store=user.store, **validated_data)
        return product 