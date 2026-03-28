from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework.permissions import IsAuthenticated
from .services import create_order_service
from django.core.exceptions import ValidationError
from django.shortcuts import render
from .models import Order
from rest_framework import generics
from .serializers import OrderSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework import status

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
        # Admin được xem tất cả, User thường chỉ xem của chính mình
        user = self.request.user
        if getattr(user, 'role', '') == 'admin' or user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)
    
def history_page(request):
    return render(request, 'history.html')

def history_detail_page(request, pk):
    # Truyền order_id sang template để JS sử dụng gọi API
    return render(request, 'history_detail.html', {'order_id': pk})

# ADMIN
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# 1. Thêm View render trang HTML
def admin_order_page(request):
    """Render trang HTML quản lý đơn hàng cho Admin"""
    return render(request, 'admin/orders.html')

# 2. Thêm API lấy danh sách đơn hàng cho Admin
class AdminOrderListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # Chỉ cho phép Admin xem
        if getattr(self.request.user, 'role', '') == 'admin' or self.request.user.is_staff:
            return Order.objects.all().order_by('-created_at')
        return Order.objects.none()

    # THÊM HÀM NÀY ĐỂ CẬP NHẬT TRẠNG THÁI
    def patch(self, request, *args, **kwargs):
        order_id = request.data.get('order_id')
        new_status = request.data.get('status')
        
        try:
            order = Order.objects.get(id=order_id)
            order.status = new_status
            order.save()
            # Quan trọng: Trả về JSON để JS không bị lỗi 'Unexpected token'
            return Response({"message": "Thành công"}, status=200)
        except Order.DoesNotExist:
            return Response({"error": "Không tìm thấy đơn hàng"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)