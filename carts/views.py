from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, get_object_or_404
from .models import Cart, CartItem
from .serializers import CartSerializer
from products.models import Product

# ===========================
# 1. API VIEWS (Trả về JSON)
# ===========================

class CartAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Lấy giỏ hàng"""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return Response(CartSerializer(cart).data)

    def delete(self, request):
        """Xóa sạch giỏ hàng"""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        return Response({"message": "Cart cleared"}, status=status.HTTP_200_OK)

class AddToCartAPI(APIView):
    permission_classes = [IsAuthenticated] # Bắt buộc đăng nhập

    def post(self, request):
        product_id = request.data.get('product_id')
        try:
            quantity = int(request.data.get('quantity', 1))
        except:
            quantity = 1

        # 1. Kiểm tra sản phẩm
        product = get_object_or_404(Product, pk=product_id)

        # 2. Lấy hoặc tạo giỏ hàng cho user
        cart, _ = Cart.objects.get_or_create(user=request.user)

        # 3. Thêm sản phẩm vào giỏ (hoặc cập nhật số lượng)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
            
        cart_item.save()

        return Response({"message": "Đã thêm vào giỏ"}, status=status.HTTP_200_OK)

class UpdateCartItemAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Cập nhật số lượng"""
        item_id = request.data.get('item_id')
        try:
            quantity = int(request.data.get('quantity'))
        except:
             return Response({"error": "Số lượng không hợp lệ"}, status=400)
        
        cart = get_object_or_404(Cart, user=request.user)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)

        if quantity > 0:
            item.quantity = quantity
            item.save()
        else:
            item.delete()

        # Trả về data giỏ hàng mới nhất để frontend cập nhật luôn
        return Response(CartSerializer(cart).data)

# ===========================
# 2. HTML VIEW (Trả về Giao diện)
# ===========================

def cart_page(request):
    return render(request, 'carts.html')