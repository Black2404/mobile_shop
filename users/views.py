from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegisterSerializer, LoginSerializer
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from .serializers import UserUpdateSerializer
from .models import User
from products.models import Product
from orders.models import Order
from reviews.models import Review

# --- API AUTH ---
class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Đăng ký thành công"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        data = {"id": user.id, "name": user.name, "email": user.email, "role": user.role, "address": user.address}
        return Response(data)

# --- API ADMIN DASHBOARD (Cập nhật logic mới) ---

class AdminStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'admin' and not request.user.is_superuser:
            return Response(status=403)

        # 1. User Stats
        total_users = User.objects.count()
        last_month = timezone.now() - timedelta(days=30)
        new_users = User.objects.filter(created_at__gte=last_month).count()
        active_users = User.objects.filter(is_active=True).count()
        admin_count = User.objects.filter(role='admin').count()

        # 2. Product Stats
        total_products = Product.objects.count()
        active_products = total_products 

        # 3. Order Stats (Lưu ý trạng thái PENDING viết hoa theo model mới)
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='PENDING').count()

        # 4. Review Stats
        total_reviews = Review.objects.count()
        avg_rating_data = Review.objects.aggregate(Avg('rating'))
        avg_rating = round(avg_rating_data['rating__avg'] or 0, 1)

        return Response({
            "total_users": total_users,
            "new_users_30_days": new_users,
            "active_users": active_users,
            "admin_count": admin_count,
            "products": {
                "total": total_products,
                "active": active_products
            },
            "orders": {
                "total": total_orders,
                "pending": pending_orders
            },
            "reviews": {
                "total": total_reviews,
                "avg_rating": avg_rating
            }
        }, status=status.HTTP_200_OK)

class AdminUserListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if request.user.role != 'admin': return Response(status=403)
        users = User.objects.all().order_by('-created_at').values('id', 'name', 'email', 'role', 'address', 'is_active', 'created_at')
        return Response(list(users), status=200)

class AdminUserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(User, pk=pk)

    def get(self, request, pk):
        if request.user.role != 'admin':
            return Response(status=403)
        user = self.get_object(pk)
        # Tái sử dụng UserProfileView logic hoặc trả về data trực tiếp
        data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "address": user.address,
            "is_active": user.is_active
        }
        return Response(data)

    def put(self, request, pk):
        if request.user.role != 'admin':
            return Response(status=403)
        
        user = self.get_object(pk)
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Cập nhật thành công!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if request.user.role != 'admin':
            return Response(status=403)
        
        user = self.get_object(pk)
        
        # Ngăn admin tự xóa chính mình
        if user.id == request.user.id:
             return Response({"error": "Không thể tự xóa tài khoản đang đăng nhập"}, status=400)

        user.delete()
        return Response({"message": "Đã xóa người dùng"}, status=status.HTTP_204_NO_CONTENT)
    
class AdminOrderListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if request.user.role != 'admin': return Response(status=403)
        
        # Lưu ý: User trong Order tham chiếu tới settings.AUTH_USER_MODEL
        orders = Order.objects.all().order_by('-created_at')
        data = []
        for o in orders:
            data.append({
                'id': o.id,
                'user__name': o.user.name if o.user else "Unknown", # Truy cập quan hệ FK
                'total_price': o.total_price,
                'status': o.status,
                'created_at': o.created_at
            })
        return Response(data, status=200)


# --- FRONTEND VIEWS (Giữ nguyên) ---
def login_page(request): return render(request, 'auth/login.html')
def register_page(request): return render(request, 'auth/register.html')
def home(request): return render(request, 'home.html')
def profile_page(request): return render(request, 'profile.html')
def dashboard_page(request): return render(request, 'admin/dashboard.html')
def admin_users_page(request): return render(request, 'admin/users.html')
