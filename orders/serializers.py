from rest_framework import serializers
from .models import Order, OrderItem
# 1. Import model ProductImage từ app products (quan trọng)
from products.models import ProductImage 

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    # 2. SỬA: Dùng SerializerMethodField để tự viết logic lấy ảnh
    product_image = serializers.SerializerMethodField()
    
    sub_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['product_id', 'product_name', 'product_image', 'price', 'quantity', 'sub_total']

    def get_sub_total(self, obj):
        return obj.price * obj.quantity

    # 3. Logic lấy ảnh (Copy logic từ ProductSerializer sang đây)
    def get_product_image(self, obj):
        # obj là OrderItem -> obj.product là sản phẩm
        img = ProductImage.objects.filter(product=obj.product).first()
        
        if img:
            # Trả về đường dẫn ảnh chuẩn như bên trang sản phẩm
            return f"/static/images/{img.image_url}"
        
        # Trả về None hoặc ảnh mặc định nếu không tìm thấy
        return "https://placehold.co/60x60?text=No+Img"

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    # Lấy tên thật của người dùng (user.name)
    customer_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'total_price', 'status', 'shipping_address', 'created_at', 'items', 'customer_name']