from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework.permissions import IsAuthenticated
from .services import create_order_service
from django.core.exceptions import ValidationError
from django.shortcuts import render
from .models import Order
from rest_framework import generics
from .serializers import OrderSerializer, OrderItemSerializer 

# THANH TOÁN
class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Lấy thông tin từ request
        shipping_address = request.data.get('shipping_address')

        # Validate cơ bản
        if not shipping_address:
            return Response(
                {"error": "Vui lòng cung cấp địa chỉ giao hàng (shipping_address)."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Gọi service xử lý
            order = create_order_service(
                user=request.user, 
                shipping_address=shipping_address
            )

            # Trả về kết quả
            return Response({
                "message": "Tạo đơn hàng thành công!",
                "order_id": order.id,
                "total_price": order.total_price,
                "status": order.status
            }, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({"error": e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Lỗi chi tiết:", str(e)) 
            return Response({"error": f"Lỗi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
def checkout_page(request):
    return render(request, 'checkout.html')

# XEM LỊCH SỬ ĐƠN HÀNG
class OrderHistoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        # Lấy tất cả đơn hàng của user hiện tại, sắp xếp mới nhất lên đầu
        return Order.objects.filter(user=self.request.user).order_by('-created_at').prefetch_related('items__product')

# XEM CHI TIẾT ĐƠN HÀNG
class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        # Chỉ cho phép user xem đơn hàng của chính họ
        return Order.objects.filter(user=self.request.user)
    
def history_page(request):
    return render(request, 'history.html')

def history_detail_page(request, pk):
    # Truyền order_id sang template để JS sử dụng gọi API
    return render(request, 'history_detail.html', {'order_id': pk})