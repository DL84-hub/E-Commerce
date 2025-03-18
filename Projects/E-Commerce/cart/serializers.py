from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import ProductSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']
        read_only_fields = ['id', 'total_price']
    
    def get_total_price(self, obj):
        return obj.total_price

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'total_items']
        read_only_fields = ['id', 'total_price', 'total_items']
    
    def get_total_price(self, obj):
        return obj.total_price
    
    def get_total_items(self, obj):
        return obj.total_items 