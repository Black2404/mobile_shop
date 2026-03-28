from rest_framework import serializers
from .models import Review, CustomUser

class ReviewSerializer(serializers.ModelSerializer):
    
    user_name = serializers.SerializerMethodField()

    def get_user_name(self, obj):
        try:
            user = CustomUser.objects.get(id=obj.user_id)
            return user.name
        except CustomUser.DoesNotExist:
            return None
    product_name = serializers.ReadOnlyField(source='product.name') 

    class Meta:
        model = Review
        fields = ['id', 'product', 'product_name', 'user', 'user_name', 'rating', 'comment', 'admin_reply', 'created_at']
        read_only_fields = ['user', 'created_at']