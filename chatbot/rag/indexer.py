from django.db import connection
from django.db.models import Sum, Avg, Count
from chatbot.rag.embedder import embed_text

# Import Models
from products.models import Product, ProductSpec
from orders.models import OrderItem
from reviews.models import Review

# 1. HÀM PHỤ TRỢ: TẠO NỘI DUNG TEXT (Dùng chung)
def generate_product_content(p):
    """
    Nhận vào object Product -> Trả về text mô tả đầy đủ để AI học.
    Hàm này tách riêng để logic đồng nhất, sửa 1 nơi áp dụng cho tất cả.
    """
    # A. Thương hiệu
    brand_name = p.brand.name if p.brand else "Không rõ thương hiệu"

    # B. Tính lượt mua 
    sales_data = OrderItem.objects.filter(product=p).aggregate(Sum('quantity'))
    total_sold = sales_data['quantity__sum'] if sales_data['quantity__sum'] else 0

    # C. Tính đánh giá 
    review_stats = Review.objects.filter(product=p).aggregate(
        avg=Avg('rating'), 
        count=Count('id')
    )
    avg_rating = review_stats['avg'] if review_stats['avg'] else 0
    review_count = review_stats['count']

    if review_count > 0:
        review_text = f"{avg_rating:.1f}/5 sao (Dựa trên {review_count} đánh giá)"
    else:
        review_text = "Chưa có đánh giá nào."

    # D. Cấu hình 
    spec = ProductSpec.objects.filter(product=p).first()
    if spec:
        spec_info = f"""
        - Màn hình: {spec.screen}
        - CPU: {spec.cpu} | RAM: {spec.ram} | Bộ nhớ: {spec.storage}
        - Pin: {spec.battery} | Camera: {spec.camera}
        - Hệ điều hành: {spec.os}
        """
    else:
        spec_info = "Thông số kỹ thuật đang cập nhật."

    # E. Ghép thành văn bản hoàn chỉnh
    text = f"""
    Tên sản phẩm: {p.name}
    Thương hiệu: {brand_name}
    Giá bán: {p.price:,} VNĐ
    
    Dữ liệu thị trường:
    - Số lượng đã bán: {total_sold}
    - Đánh giá khách hàng: {review_text}
    
    Cấu hình chi tiết:
    {spec_info}
    
    Mô tả sản phẩm:
    {p.description}
    """
    
    # Trả về text và các chỉ số phụ để log ra màn hình
    return text, total_sold, avg_rating

# 2. HÀM CHÍNH: CẬP NHẬT 1 SẢN PHẨM (Dùng cho Signals)
def index_single_product(product_id):
    try:
        # Lấy sản phẩm từ DB
        p = Product.objects.get(id=product_id)
        
        # 1. Tạo nội dung (Gọi hàm phụ trợ ở trên)
        text, total_sold, rating = generate_product_content(p)

        # 2. Mã hóa (Embedding)
        emb = embed_text(text)

        # 3. Cập nhật vào Database Vector
        with connection.cursor() as cursor:
            # Xóa bản ghi cũ để tránh trùng lặp
            cursor.execute("DELETE FROM product_embeddings WHERE product_id = %s", [p.id])
            
            # Thêm bản ghi mới
            cursor.execute("""
                INSERT INTO product_embeddings (product_id, content, embedding)
                VALUES (%s, %s, %s)
            """, [p.id, text, emb])
            
        print(f"Đã cập nhật: {p.name} | Bán: {total_sold} | Rate: {rating:.1f}⭐")

    except Product.DoesNotExist:
        print(f"Không tìm thấy sản phẩm ID {product_id} để cập nhật.")
    except Exception as e:
        print(f"Lỗi khi index sản phẩm {product_id}: {e}")

# 3. HÀM CHẠY HÀNG LOẠT (Dùng khi khởi tạo lại DB)
def index_products():
    print("Bắt đầu học lại toàn bộ dữ liệu...")
    
    # Xóa sạch bảng vector trước khi chạy lại từ đầu
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM product_embeddings")

    # Lấy danh sách tất cả ID sản phẩm
    all_product_ids = Product.objects.values_list('id', flat=True)
    
    count = 0
    for pid in all_product_ids:
        # Tái sử dụng hàm index_single_product -> Code gọn, không lặp lại logic
        index_single_product(pid)
        count += 1

    print(f"Hoàn tất! Đã học xong {count} sản phẩm.")