from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet

# Tạo router
router = DefaultRouter()
# Để r'' (rỗng) để router ăn theo đường dẫn cha
router.register(r'', ReviewViewSet, basename='review')

urlpatterns = [
    # Đường dẫn API: /reviews/api/
    path('api/', include(router.urls)),
]