from django.urls import path
from .views import CreateOrderView, OrderHistoryView, OrderDetailView, checkout_page, history_page, history_detail_page, admin_order_page, AdminOrderListView

urlpatterns = [

    path('api/orders/', CreateOrderView.as_view(), name='checkout'),

    path('api/orders/history/', OrderHistoryView.as_view(), name='history'),

    path('api/orders/detail/<int:pk>/', OrderDetailView.as_view(), name='detail'),

    path('orders/checkout/', checkout_page, name='page_checkout'),
    path('orders/history/', history_page, name='page_history'),
    path('orders/detail/<int:pk>/', history_detail_page, name='page_detail'),

    path('admin/manage/', admin_order_page, name='admin_orders_html'),
    path('api/admin/list/', AdminOrderListView.as_view(), name='api_admin_order_list'),
]
    