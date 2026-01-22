from django.urls import path
from .views import (
    ProductListAPI, ProductDetailAPI, HomeProductAPI,  AdminProductDetailView, AdminProductListView,BrandListAPI,
    product_list_page, product_detail_page, admin_product_page
)

urlpatterns = [
    
    path('products/', product_list_page, name='product_list_html'),
    
    path('products/<int:pk>/', product_detail_page, name='product_detail_html'),
    
    path('api/products', ProductListAPI.as_view(), name='api_product_list'),
    
    path('api/products/<int:pk>/', ProductDetailAPI.as_view(), name='api_product_detail'),

    path('api/products/home/', HomeProductAPI.as_view(), name='api_home_product'),

    path('admin/products', admin_product_page, name='admin_products_html'),

    path('api/admin/products/', AdminProductListView.as_view(), name='api_admin_products_list'),

    path('api/admin/products/', AdminProductListView.as_view(), name='api_admin_products'),

    path('api/admin/products/<int:pk>/', AdminProductDetailView.as_view(), name='api_admin_product_detail'),

    path('api/brands/', BrandListAPI.as_view(), name='api_brand_list'),
]