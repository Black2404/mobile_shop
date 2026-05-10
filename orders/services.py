from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Order, OrderItem
from carts.models import Cart, CartItem 
from orders.signals import after_order_bulk_create
def create_order_service(user, shipping_address):
    
    try:
        cart = Cart.objects.get(user=user)
        cart_items = CartItem.objects.filter(cart=cart).select_related('product')
    except Cart.DoesNotExist:
        raise ValidationError("Không tìm thấy giỏ hàng của người dùng.")

    if not cart_items.exists():
        raise ValidationError("Giỏ hàng trống, không thể tạo đơn hàng.")

    total_order_price = 0
    order_items_to_create = []

    with transaction.atomic():
        
        order = Order.objects.create(
            user=user,
            shipping_address=shipping_address,
            status='PENDING',
            total_price=0 
        )

        for item in cart_items:
            line_total = item.product.price * item.quantity
            total_order_price += line_total

            order_items_to_create.append(
                OrderItem(
                    order=order,
                    product=item.product,
                    price=item.product.price, 
                    quantity=item.quantity
                )
            )

        OrderItem.objects.bulk_create(order_items_to_create)

        sold_product_ids = [item.product.id for item in order_items_to_create]

        print(f"Orders: Đang gửi tín hiệu cập nhật cho {len(sold_product_ids)} sản phẩm...")
        after_order_bulk_create.send(
            sender=Order, 
            product_ids=sold_product_ids
        )

        order.total_price = total_order_price
        order.save(update_fields=['total_price'])

        cart_items.delete()
        

    return order