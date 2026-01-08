from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegisterSerializer, LoginSerializer
from django.shortcuts import render
from .models import User 
from django.utils import timezone
from datetime import timedelta

# --- API VIEWS ---

class RegisterView(APIView):
    # Cho phép ai cũng được đăng ký (Không cần Token)
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Đăng ký thành công",
                "user": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    # Cho phép ai cũng được đăng nhập (Không cần Token)
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "name": request.user.name,
            "email": request.user.email,
            "role": request.user.role,
            "address": request.user.address
        })

    def put(self, request):
        user = request.user
        data = request.data

        # Cập nhật các trường cơ bản
        user.name = data.get('name', user.name)
        user.address = data.get('address', user.address)

        # Nếu có mật khẩu mới thì mã hóa và lưu
        password = data.get('password')
        if password:
            user.set_password(password)
        
        user.save()
        return Response({"message": "Cập nhật thành công"}, status=status.HTTP_200_OK)
    
class AdminUserListView(APIView):
    # Chỉ cho phép user đã đăng nhập
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Kiểm tra quyền Admin (theo logic role hoặc is_superuser)
        if request.user.role != 'admin' and not request.user.is_superuser:
            return Response(
                {"detail": "Bạn không có quyền truy cập."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # Lấy tất cả user
        users = User.objects.all().values('id', 'name', 'email', 'role', 'address', 'is_active')
        return Response(list(users), status=status.HTTP_200_OK)
    
class AdminStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 1. Check quyền Admin
        if request.user.role != 'admin' and not request.user.is_superuser:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        # 2. Tính toán số liệu
        total_users = User.objects.count()
        
        # User đăng ký trong 30 ngày qua
        last_month = timezone.now() - timedelta(days=30)
        new_users = User.objects.filter(created_at__gte=last_month).count()

        # User đang hoạt động (active)
        active_users = User.objects.filter(is_active=True).count()

        # Admin users
        admin_count = User.objects.filter(role='admin').count()

        return Response({
            "total_users": total_users,
            "new_users_30_days": new_users,
            "active_users": active_users,
            "admin_count": admin_count
        }, status=status.HTTP_200_OK)

# --- FRONTEND VIEWS ---

def login_page(request):
    return render(request, 'auth/login.html')

def register_page(request):
    return render(request, 'auth/register.html')

def home(request):
    return render(request, 'home.html')

def profile_page(request):
    return render(request, 'profile.html')

def dashboard_page(request):
    return render(request, 'admin/dashboard.html')