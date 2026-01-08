from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import ProductSerializer

class CartItemSerializer(serializers.ModelSerializer):
    # Lấy chi tiết sản phẩm (tên, ảnh, giá) để hiển thị
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    
    # --- SỬA: Ánh xạ từ total_price của Model sang sub_total của API ---
    sub_total = serializers.ReadOnlyField(source='total_price')

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'sub_total']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    
    # Lấy từ hàm total_price trong model Cart vừa thêm
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price', 'created_at']