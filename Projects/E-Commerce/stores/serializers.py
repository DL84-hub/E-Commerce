from rest_framework import serializers
from .models import Store
from users.serializers import UserSerializer

class StoreSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    
    class Meta:
        model = Store
        fields = ['id', 'owner', 'name', 'description', 'address', 'phone_number', 'email', 'logo', 'is_verified', 'created_at', 'updated_at']
        read_only_fields = ['id', 'is_verified', 'created_at', 'updated_at']

class StoreCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['name', 'description', 'address', 'phone_number', 'email', 'logo']
        
    def create(self, validated_data):
        user = self.context['request'].user
        store = Store.objects.create(owner=user, **validated_data)
        return store 