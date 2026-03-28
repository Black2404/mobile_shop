from django.shortcuts import render
from rest_framework import viewsets, permissions, pagination
from .models import Review
from .serializers import ReviewSerializer
from rest_framework import filters
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

# 1. CẤU HÌNH PHÂN TRANG (10 dòng/trang)
class ReviewPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('user', 'product').all()
    serializer_class = ReviewSerializer
    pagination_class = ReviewPagination # Kích hoạt phân trang
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter] 
    search_fields = ['product__name', 'user__name', 'comment']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # HỖ TRỢ LỌC DỮ LIỆU
    def get_queryset(self):
    # Sử dụng self.queryset đã khai báo select_related ở trên thay vì gọi super() để tránh truy vấn lại
        qs = self.queryset 
        
        p_id = self.request.query_params.get('product_id')
        if p_id:
            qs = qs.filter(product_id=p_id)
            
        rating = self.request.query_params.get('rating')
        if rating:
            # Ép kiểu để tránh lỗi nếu giá trị truyền vào không phải là số
            try:
                qs = qs.filter(rating=int(rating))
            except ValueError:
                pass
                
        return qs
    

    def destroy(self, request, *args, **kwargs):
        review = self.get_object()

        if review.user != request.user and not request.user.is_staff:
            raise PermissionDenied("Bạn không có quyền xóa")

        review.delete()

        return Response(
            {"message": "Xóa đánh giá thành công"},
            status=status.HTTP_200_OK
        )


def admin_reviews_html(request):
    return render(request, 'admin/reviews.html')