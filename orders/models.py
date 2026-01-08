# orders/models.py
from django.db import models
from django.conf import settings  # Quan trọng: Dùng để tham chiếu tới model User chuẩn
from django.utils import timezone

class Order(models.Model):
    # Các lựa chọn trạng thái đơn hàng
    STATUS_CHOICES = [
        ('PENDING', 'Chờ xử lý'),
        ('COMPLETED', 'Đã hoàn thành'),
        ('CANCELLED', 'Đã hủy'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='orders'
    )
    
    total_price = models.BigIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    shipping_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'orders'

    def __str__(self):
        # self.user.username vẫn hoạt động bình thường
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items' # Giúp truy vấn ngược: order.items.all()
    )
    # Giả sử model Product nằm trong app 'products'
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    
    price = models.BigIntegerField()
    quantity = models.IntegerField(default=1)

    class Meta:
        db_table = 'order_items'