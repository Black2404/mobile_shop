from django.dispatch import receiver
from chatbot.rag.indexer import index_single_product
from django.db.models.signals import post_save, post_delete
from django.db import connection, transaction  # <--- THÊM transaction

# Import tín hiệu từ các module
from orders.signals import after_order_bulk_create
from reviews.models import Review
from products.models import Product, ProductSpec

# CẬP NHẬT ORDERS
@receiver(after_order_bulk_create)
def handle_bulk_order(sender, product_ids, **kwargs):
    if product_ids:
        unique_ids = set(product_ids)
        print(f"Chatbot: Nhận tín hiệu Order. Đợi commit DB để học {len(unique_ids)} sản phẩm...")
        
        # Dùng lambda để trì hoãn việc chạy cho đến khi DB commit xong
        transaction.on_commit(lambda: [index_single_product(pid) for pid in unique_ids])

# CẬP NHẬT REVIEWS
@receiver([post_save, post_delete], sender=Review)
def handle_review_change(sender, instance, **kwargs):
    if instance.product:
        print(f"Review thay đổi. Đợi commit để tính lại điểm cho: {instance.product.name}")
        # Chờ commit xong mới chạy
        transaction.on_commit(lambda: index_single_product(instance.product.id))

# CẬP NHẬT PRODUCTS
@receiver(post_save, sender=Product)
def handle_product_save(sender, instance, **kwargs):
    print(f"Admin sửa sản phẩm {instance.name}. Đợi commit...")
    # Chờ commit xong mới chạy
    transaction.on_commit(lambda: index_single_product(instance.id))

# CẬP NHẬT THÔNG SỐ KỸ THUẬT
@receiver(post_save, sender=ProductSpec)
def handle_spec_save(sender, instance, **kwargs):
    if instance.product:
        print(f"Spec thay đổi. Đợi commit...")
        # Chờ commit xong mới chạy
        transaction.on_commit(lambda: index_single_product(instance.product.id))

# KHI XÓA SẢN PHẨM (Xóa thì không cần chờ commit vì nó bay màu rồi)
@receiver(post_delete, sender=Product)
def handle_product_delete(sender, instance, **kwargs):
    print(f"Sản phẩm {instance.name} đã xóa. Xóa ngay khỏi vector DB...")
    # Đoạn này giữ nguyên hoặc cũng đưa vào on_commit tùy logic, nhưng thường xóa thì làm luôn được
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM product_embeddings WHERE product_id = %s", [instance.id])