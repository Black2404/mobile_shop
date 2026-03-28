from products.models import Product, ProductSpec
from reviews.models import Review
from orders.models import Order, OrderItem
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, F
from django.utils import timezone

User = get_user_model()

# --- NHÓM 1: QUẢN LÝ SẢN PHẨM ---
def get_product_inventory():
    """Lấy danh sách sản phẩm kèm thương hiệu và thông số kỹ thuật."""
    # Sử dụng select_related để lấy brand và prefetch_related hoặc lọc spec
    products = Product.objects.all().select_related('brand')
    res = "Danh sách sản phẩm chi tiết:\n"
    
    for p in products:
        # Lấy thông số kỹ thuật từ bảng ProductSpec
        spec = ProductSpec.objects.filter(product=p).first()
        if spec:
            spec_info = f"CPU: {spec.cpu}, RAM: {spec.ram}, Screen: {spec.screen}, Pin: {spec.battery}"
        else:
            spec_info = "Chưa cập nhật thông số"
        
        res += (f"- ID {p.id}: {p.name} [Hãng: {p.brand.name}]\n"
                f"  Giá: {p.price:,}₫ | Chi tiết: {spec_info}\n")
    return res

def get_products_by_brand(brand_name):
    """Lấy danh sách sản phẩm theo tên thương hiệu (hãng)."""
    
    products = Product.objects.filter(brand__name__icontains=brand_name).select_related('brand')
    
    if not products.exists():
        return f"Không tìm thấy hãng nào hoặc sản phẩm nào thuộc hãng: {brand_name}"
    
    brand_actual_name = products.first().brand.name
    res = f"### Danh sách sản phẩm thuộc hãng {brand_actual_name}:\n"
    for p in products:
        spec = ProductSpec.objects.filter(product=p).first()
        spec_info = f"{spec.cpu}, {spec.ram} RAM" if spec else "Chưa cập nhật cấu hình"
        
        res += (f"- **ID {p.id}**: {p.name}\n"
                f"  Giá: {p.price:,}₫ | Cấu hình: {spec_info}\n")
    return res

def update_product_detail(product_id, **kwargs):
    """Sửa tên, giá hoặc mô tả sản phẩm."""
    try:
        p = Product.objects.get(id=product_id)
        for key, value in kwargs.items():
            if hasattr(p, key): setattr(p, key, value)
        p.save()
        return f"Thành công: Đã cập nhật sản phẩm {p.name}."
    except Exception as e: return f"Lỗi: {str(e)}"

# --- NHÓM 2: QUẢN LÝ NGƯỜI DÙNG ---
def get_all_users():
    """Xem danh sách khách hàng (role='customer') và địa chỉ của họ."""
    # Lọc theo role là khách hàng và lấy thêm trường address
    users = User.objects.filter(role='customer').values('id', 'name', 'email', 'address', 'is_active')
    
    if not users:
        return "Không có người dùng nào có vai trò là khách hàng."
        
    res = "Danh sách khách hàng:\n"
    for u in users:
        status = "Active" if u['is_active'] else "Blocked"
        res += (f"- ID {u['id']}: {u['name']} ({u['email']})\n"
                f"  Địa chỉ: {u['address'] or 'Chưa cập nhật'} | Trạng thái: {status}\n")
    return res

def update_user_status(user_id, is_active: bool):
    """Khóa hoặc mở khóa tài khoản người dùng."""
    try:
        user = User.objects.get(id=user_id)
        user.is_active = is_active
        user.save()
        return f"Thành công: Đã {'mở khóa' if is_active else 'khóa'} user {user.name}."
    except Exception as e: return f"Lỗi: {str(e)}"

# --- NHÓM 3: QUẢN LÝ ĐƠN HÀNG ---

# chuyển từ ngữ con người cho khớp dữ liệu trong DB
STATUS_MAP = {
    "chờ xử lý": "PENDING",
    "đang giao": "SHIPPING",
    "đã hoàn thành": "COMPLETED",
    "đã hủy": "CANCELLED"
}

def get_recent_orders(status=None):
    """Lấy danh sách đơn hàng định dạng đẹp như ảnh mẫu."""
    orders = Order.objects.all().order_by('-created_at')
    
    if status:
        db_status = STATUS_MAP.get(status.lower())
        if db_status:
            orders = orders.filter(status=db_status)
        else:
            return f"Trạng thái '{status}' không hợp lệ."

    if not orders.exists():
        return f"Không có đơn hàng nào."

    res = f"### Tìm thấy {orders.count()} đơn hàng :\n"
    for o in orders:
        # Lấy nhãn tiếng Việt từ models.py (Chờ xử lý, Đang giao...)
        status_vn = o.get_status_display()
        
        # Định dạng chuỗi y hệt ảnh image_b9ad5e.png
        res += (f"- **Đơn #{o.id}**: {o.total_price:,}₫ | "
                f"Trạng thái: **{status_vn}** | Địa chỉ: {o.shipping_address}\n")
    return res

def update_order_status(order_id, new_status):
    """Cập nhật trạng thái và trả về thông báo tiếng Việt."""
    try:
        order = Order.objects.get(id=order_id)
        
        # Dịch từ tiếng Việt người dùng nói sang mã DB (SHIPPING, PENDING...)
        db_status = STATUS_MAP.get(new_status.lower(), new_status.upper())
        
        order.status = db_status
        order.save()
        
        return f"Thành công: Đơn hàng #{order.id} đã chuyển sang **{order.get_status_display()}**."
    except Exception as e:
        return f"Lỗi: {str(e)}"

# --- NHÓM 4: QUẢN LÝ ĐÁNH GIÁ ---

def get_product_reviews(rating=None):
    """Xem danh sách đánh giá, có thể lọc theo số sao (1-5)."""
    # Lấy reviews kèm thông tin người dùng và sản phẩm để AI có ngữ cảnh phản hồi
    reviews = Review.objects.all().select_related('user', 'product').order_by('-created_at')
    
    if rating:
        reviews = reviews.filter(rating=rating)
        
    if not reviews.exists():
        return f"Không có đánh giá nào {f'mức {rating} sao' if rating else ''}."

    res = f"Danh sách đánh giá {f'({rating} sao)' if rating else ''}:\n"
    for r in reviews:
        status = " (Đã phản hồi)" if r.admin_reply else " (Chưa phản hồi)"
        res += (f"- ID {r.id}: {r.user.name} đánh giá {r.rating} sao cho {r.product.name}\n"
                f"  Nội dung: {r.comment}\n"
                f"  Phản hồi hiện tại: {r.admin_reply or 'N/A'}{status}\n")
    return res

def reply_to_review(review_id, reply_text):
    """Gửi phản hồi của admin cho một đánh giá cụ thể."""
    try:
        review = Review.objects.get(id=review_id)
        review.admin_reply = reply_text
        review.save()
        return f"Thành công: Đã phản hồi đánh giá của {review.user.name}."
    except Review.DoesNotExist:
        return f"Lỗi: Không tìm thấy đánh giá ID {review_id}."
    except Exception as e:
        return f"Lỗi hệ thống: {str(e)}"