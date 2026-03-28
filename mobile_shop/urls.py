from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    
    # --- ĐƯỜNG DẪN CHUNG ---
    path('', include('users.urls')),
    path('', include('products.urls')),
    path('reviews/', include('reviews.urls')),
    path('carts/', include('carts.urls')),
    path('chatbot/', include('chatbot.urls')),
    path('', include('orders.urls')),
    
]