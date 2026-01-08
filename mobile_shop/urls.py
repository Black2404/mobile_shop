from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- ĐƯỜNG DẪN CHUNG ---
    path('', include('users.urls')),
    path('products/', include('products.urls')), 
    path('reviews/', include('reviews.urls')),
    path('carts/', include('carts.urls')),
    path('chatbot/', include('chatbot.urls')),
    path('orders/', include('orders.urls')),
    
]