# orders/signals.py
from django.dispatch import Signal

# Định nghĩa tín hiệu: "Đã tạo xong đơn hàng số lượng lớn"
after_order_bulk_create = Signal()