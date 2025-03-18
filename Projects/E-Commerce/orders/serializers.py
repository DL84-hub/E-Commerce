from rest_framework import serializers
from .models import Order, OrderItem
from users.serializers import UserSerializer
from products.serializers import ProductSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'total_price']
        read_only_fields = ['id', 'price', 'total_price']

class OrderSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'customer', 'order_number', 'status', 'total_amount', 'shipping_address', 'payment_status', 'created_at', 'updated_at', 'items']
        read_only_fields = ['id', 'order_number', 'created_at', 'updated_at']

class OrderCreateSerializer(serializers.ModelSerializer):
    items = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField(),
            allow_empty=False
        ),
        required=True
    )
    
    class Meta:
        model = Order
        fields = ['shipping_address', 'items']
        
    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Order must contain at least one item.")
        return value
        
    def create(self, validated_data):
        from products.models import Product
        import uuid
        
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        
        # Generate a unique order number
        order_number = str(uuid.uuid4()).split('-')[0].upper()
        
        # Calculate total amount
        total_amount = 0
        for item in items_data:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)
            
            try:
                product = Product.objects.get(id=product_id, is_active=True)
                if product.stock < quantity:
                    raise serializers.ValidationError(f"Not enough stock for {product.name}.")
                
                total_amount += product.price * quantity
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Product with ID {product_id} does not exist.")
        
        # Create order
        order = Order.objects.create(
            customer=user,
            order_number=order_number,
            total_amount=total_amount,
            shipping_address=validated_data.get('shipping_address'),
        )
        
        # Create order items
        for item in items_data:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)
            
            product = Product.objects.get(id=product_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )
            
            # Update product stock
            product.stock -= quantity
            product.save()
        
        return order

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status'] 