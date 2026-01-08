from rest_framework import viewsets, permissions
from .models import Review
from .serializers import ReviewSerializer

# Permission tùy chỉnh: Chỉ chủ sở hữu mới được Sửa/Xóa
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    
    # Kết hợp: Đăng nhập mới được Comment, Chính chủ mới được Xóa
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        """
        Hỗ trợ lọc theo product_id để hiển thị ở trang chi tiết
        URL: /reviews/api/?product_id=5
        """
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

    def perform_create(self, serializer):
        # Tự động gán user đang đăng nhập vào review
        serializer.save(user=self.request.user)