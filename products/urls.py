from django.urls import path
from .views import (
    ProductListAPI, 
    ProductDetailAPI, 
    HomeProductAPI, 
    product_list_page, 
    product_detail_page
)

urlpatterns = [
    # ==============================
    # 1. FRONTEND (Trả về HTML)
    # ==============================
    
    # Đường dẫn: /products/
    path('', product_list_page, name='product_list_html'),
    
    # Đường dẫn: /products/1/
    path('<int:pk>/', product_detail_page, name='product_detail_html'),

    # ==============================
    # 2. API (Trả về JSON)
    # ==============================
    
    # Đường dẫn: /products/api/
    path('api/', ProductListAPI.as_view(), name='api_product_list'),
    
    # Đường dẫn: /products/api/1/
    path('api/<int:pk>/', ProductDetailAPI.as_view(), name='api_product_detail'),
    
    # Đường dẫn: /products/api/home/
    path('api/home/', HomeProductAPI.as_view(), name='api_home_product'),
]