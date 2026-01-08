from django.urls import path
from .views import CreateOrderView, OrderHistoryView, OrderDetailView, checkout_page, history_page, history_detail_page

app_name = 'orders'

urlpatterns = [
    # Endpoint: orders/api/checkout/
    path('api/', CreateOrderView.as_view(), name='checkout'),
    # GET orders/api/history/ -> Trả về danh sách đơn hàng
    path('api/history/', OrderHistoryView.as_view(), name='history'),
    # GET orders/api/detail/12/ -> Trả về chi tiết đơn hàng ID 12
    path('api/detail/<int:pk>/', OrderDetailView.as_view(), name='detail'),

    path('checkout/', checkout_page, name='page_checkout'),
    path('history/', history_page, name='page_history'),
    path('detail/<int:pk>/', history_detail_page, name='page_detail'),
]