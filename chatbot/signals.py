from django.dispatch import receiver
from chatbot.rag.indexer import index_single_product
from django.db.models.signals import post_save, post_delete
from django.db import connection

# Import tín hiệu từ các module
from orders.signals import after_order_bulk_create
from reviews.models import Review
from products.models import Product, ProductSpec

# CẬP NHẬT ORDERS
@receiver(after_order_bulk_create)
def handle_bulk_order(sender, product_ids, **kwargs):
    """
    Hàm này tự động chạy khi Orders bắn tín hiệu
    """
    print(f"Chatbot: Đã nhận tín hiệu! Đang cập nhật kiến thức cho {len(product_ids)} sản phẩm...")
    
    if product_ids:
        # Loại bỏ ID trùng lặp nếu khách mua 2 dòng cùng 1 sản phẩm (ít gặp nhưng cứ đề phòng)
        unique_ids = set(product_ids)
        for pid in unique_ids:
            index_single_product(pid)

# CẬP NHẬT REVIEWS
@receiver([post_save, post_delete], sender=Review)
def handle_review_change(sender, instance, **kwargs):
    """
    Hàm này tự chạy khi user bình luận hoặc xóa bình luận.
    instance: chính là object Review vừa thao tác.
    """
    if instance.product:
        print(f"Review thay đổi cho SP: {instance.product.name}. AI đang tính lại điểm đánh giá...")
        # Gọi hàm học lại đúng 1 sản phẩm này
        index_single_product(instance.product.id)

# CẬP NHẬT PRODUCTS
# Khi thêm mới hoặc sửa thông tin Sản phẩm (Tên, Giá, Mô tả...)
@receiver(post_save, sender=Product)
def handle_product_save(sender, instance, **kwargs):
    print(f"Admin vừa cập nhật sản phẩm: {instance.name}. Đang học lại...")
    index_single_product(instance.id)

# Khi sửa thông số kỹ thuật (RAM, Chip, Màn hình...)
@receiver(post_save, sender=ProductSpec)
def handle_spec_save(sender, instance, **kwargs):
    # ProductSpec gắn với Product qua khóa ngoại 'product'
    if instance.product:
        print(f"Thông số kỹ thuật thay đổi cho SP ID {instance.product.id}. Đang học lại...")
        index_single_product(instance.product.id)

# Khi xóa sản phẩm
@receiver(post_delete, sender=Product)
def handle_product_delete(sender, instance, **kwargs):
    print(f"Sản phẩm {instance.name} đã bị xóa. Đang xóa khỏi bộ nhớ AI...")
    # Vì sản phẩm đã mất trong DB, ta không thể gọi index_single_product được
    # Phải xóa thủ công trong bảng vector
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM product_embeddings WHERE product_id = %s", [instance.id])