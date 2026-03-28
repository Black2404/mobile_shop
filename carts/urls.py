from django.urls import path
from .views import (
    CartAPI, 
    AddToCartAPI, 
    UpdateCartItemAPI, 
    cart_page
)

urlpatterns = [
    # --- GIAO DIỆN HTML ---
    # Đường dẫn: /carts/
    path('', cart_page, name='cart_page'),

    # --- API (JSON) ---
    # Đường dẫn: /carts/api/ (Lấy danh sách & Xóa)
    path('api/', CartAPI.as_view(), name='api_cart_list'),          
    
    # Đường dẫn: /carts/api/add/ (Thêm sản phẩm)
    path('api/add/', AddToCartAPI.as_view(), name='api_add_cart'),
    
    # Đường dẫn: /carts/api/update/ (Cập nhật số lượng)
    path('api/update/', UpdateCartItemAPI.as_view(), name='api_cart_update'), 
]