from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet, admin_reviews_html

router = DefaultRouter()
router.register(r'', ReviewViewSet, basename='review')

urlpatterns = [
    # Trang đánh giá
    path('api/', include(router.urls)),
    
    # Trang quản lý đánh giá
    path('dashboard/', admin_reviews_html, name='admin_reviews_html'),
]