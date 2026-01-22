from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Order, OrderItem
from carts.models import Cart, CartItem 
from orders.signals import after_order_bulk_create
def create_order_service(user, shipping_address):
    
    # 1. Lấy dữ liệu giỏ hàng
    try:
        cart = Cart.objects.get(user=user)
        # Dùng select_related để lấy luôn thông tin product, tránh n+1 query
        cart_items = CartItem.objects.filter(cart=cart).select_related('product')
    except Cart.DoesNotExist:
        raise ValidationError("Không tìm thấy giỏ hàng của người dùng.")

    if not cart_items.exists():
        raise ValidationError("Giỏ hàng trống, không thể tạo đơn hàng.")

    total_order_price = 0
    order_items_to_create = []

    # 2. Bắt đầu Transaction (Để đảm bảo Order và OrderItems được tạo đồng bộ) -> nếu sai thì rollback
    with transaction.atomic():
        # A. Tạo Order Header trước
        order = Order.objects.create(
            user=user,
            shipping_address=shipping_address,
            status='PENDING',
            total_price=0 # Tạm thời để 0, update sau
        )

        # B. Chuẩn bị dữ liệu Order Items
        for item in cart_items:
            # Tính toán tiền (Giá sản phẩm * số lượng)
            # Lưu ý: Không cần check product.stock hay trừ stock ở đây nữa
            line_total = item.product.price * item.quantity
            total_order_price += line_total

            # Tạo đối tượng OrderItem (nhưng chưa lưu xuống DB ngay để dùng bulk_create)
            order_items_to_create.append(
                OrderItem(
                    order=order,
                    product=item.product,
                    price=item.product.price, # Quan trọng: Lưu giá gốc
                    quantity=item.quantity
                )
            )

        # C. Lưu tất cả Order Items cùng lúc (Tối ưu SQL) -> gom nhiều đơn hàng trong 1 giỏ hàng lại rồi gửi 1 lần
        OrderItem.objects.bulk_create(order_items_to_create)

        # Lấy danh sách ID các sản phẩm vừa bán để báo cho ai cần biết
        sold_product_ids = [item.product.id for item in order_items_to_create]
        
        # BẮN TÍN HIỆU: "Tôi vừa bán xong các sản phẩm này, ai làm gì thì làm"
        print(f"Orders: Đang gửi tín hiệu cập nhật cho {len(sold_product_ids)} sản phẩm...")
        after_order_bulk_create.send(
            sender=Order, 
            product_ids=sold_product_ids
        )
        # D. Cập nhật tổng tiền cho Order
        order.total_price = total_order_price
        order.save(update_fields=['total_price'])

        # E. Xóa giỏ hàng (Cleanup)
        cart_items.delete()
        

    return order