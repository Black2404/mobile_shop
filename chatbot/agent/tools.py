from products.models import Product, ProductSpec
from reviews.models import Review
from orders.models import Order, OrderItem
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, F
from datetime import timedelta, datetime
from django.db.models.functions import Coalesce
from django.db.models import Value
from chatbot.rag.retriever import search_products

User = get_user_model()

# Quản lý sản phẩm
def get_product_inventory():
    """Lấy danh sách sản phẩm kèm thương hiệu và thông số kỹ thuật."""
    # Sử dụng select_related để lấy brand và prefetch_related hoặc lọc spec
    products = Product.objects.all().select_related('brand')
    res = "Danh sách sản phẩm chi tiết:\n"
    
    for p in products:
        
        spec = ProductSpec.objects.filter(product=p).first()
        if spec:
            spec_info = f"CPU: {spec.cpu}, RAM: {spec.ram}, Screen: {spec.screen}, Pin: {spec.battery}"
        else:
            spec_info = "Chưa cập nhật thông số"
        
        res += (f"- ID {p.id}: {p.name} [Hãng: {p.brand.name}]\n"
                f"  Giá: {p.price:,}₫ | Chi tiết: {spec_info}\n")
    return res

# Quản lý hãng
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

# Quản lý người dùng
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

# Quản lý đơn hàng

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
        
        status_vn = o.get_status_display()
        
        res += (f"- **Đơn #{o.id}**: {o.total_price:,}₫ | "
                f"Trạng thái: **{status_vn}** | Địa chỉ: {o.shipping_address}\n")
    return res

def update_order_status(order_id, new_status):
    """Cập nhật trạng thái và trả về thông báo tiếng Việt."""
    try:
        order = Order.objects.get(id=order_id)
        
        db_status = STATUS_MAP.get(new_status.lower(), new_status.upper())
        
        order.status = db_status
        order.save()
        
        return f"Thành công: Đơn hàng #{order.id} đã chuyển sang **{order.get_status_display()}**."
    except Exception as e:
        return f"Lỗi: {str(e)}"

# Quản lý đánh giá

def get_product_reviews(rating=None):
    """Xem danh sách đánh giá, có thể lọc theo số sao (1-3)."""
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

# Hàm lấy đánh giá theo sao
def get_reviews_by_rating_limit(max_rating):
    """Xem danh sách đánh giá có số sao nhỏ hơn max_rating."""
    # Lọc rating < max_rating
    reviews = Review.objects.filter(rating__lt=max_rating).select_related('user', 'product')
    
    if not reviews.exists():
        return f"Không có đánh giá nào dưới {max_rating} sao."
        
    res = f"Các đánh giá dưới {max_rating} sao:\n"
    for r in reviews:
        res += (f"- {r.user.name} ({r.rating} sao) cho {r.product.name}\n"
                f"  Nội dung: {r.comment}\n")
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
    
# Hàm lấy doanh thu theo ngày
def get_revenue_by_date(date_str):
    """Tính tổng doanh thu của các đơn hàng 'Đã hoàn thành' trong ngày (định dạng YYYY-MM-DD)."""
    try:
        # Chuyển đổi string sang object date
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        
        target_statuses = ['PENDING', 'SHIPPING', 'COMPLETED']

        total = Order.objects.filter(
            created_at__date=date_obj,
            status__in=target_statuses
        ).aggregate(total=Sum('total_price'))['total'] or 0
        
        return f"Tổng doanh thu ngày {date_str} là: {total:,}₫"
    except Exception as e:
        return f"Lỗi định dạng ngày hoặc truy vấn: {str(e)}"

def get_revenue_by_month(month_str):
    """
    Tính tổng doanh thu theo tháng.
    Format: YYYY-MM (VD: 2026-04)
    """
    try:
        date_obj = datetime.strptime(month_str, "%Y-%m")

        target_statuses = ['PENDING', 'SHIPPING', 'COMPLETED']

        total = Order.objects.filter(
            created_at__year=date_obj.year,
            created_at__month=date_obj.month,
            status__in=target_statuses
        ).aggregate(
            total=Sum('total_price')
        )['total'] or 0

        return f"Tổng doanh thu tháng {month_str} là: {total:,}₫"

    except Exception as e:
        return f"Lỗi: {str(e)}"

def get_revenue_by_year(year_str):
    """
    Tính tổng doanh thu theo năm.
    Format: YYYY (VD: 2026)
    """
    try:
        year = int(year_str)

        target_statuses = ['PENDING', 'SHIPPING', 'COMPLETED']

        total = Order.objects.filter(
            created_at__year=year,
            status__in=target_statuses
        ).aggregate(
            total=Sum('total_price')
        )['total'] or 0

        return f"Tổng doanh thu năm {year} là: {total:,}₫"

    except Exception as e:
        return f"Lỗi: {str(e)}"

def get_orders_by_date(date_str):
    """
    Lấy danh sách đơn hàng theo ngày.
    Format: YYYY-MM-DD
    """
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")

        orders = Order.objects.filter(
            created_at__date=date_obj
        ).order_by('-created_at')

        if not orders.exists():
            return f"Không có đơn hàng ngày {date_str}"

        res = f"Đơn hàng ngày {date_str}:\n"

        for o in orders:

            status_vn = o.get_status_display()

            res += (
                f"- Mã đơn: {o.id}\n"
                f"  Trạng thái: {status_vn}\n"
                f"  Tổng giá: {o.total_price:,}₫\n"
            )

        res += f"\nTổng số đơn: {orders.count()}"

        return res

    except Exception as e:
        return f"Lỗi: {str(e)}"

def get_orders_by_month(month_str):
    """
    Lấy đơn hàng theo tháng.
    Format: YYYY-MM
    """
    try:
        date_obj = datetime.strptime(month_str, "%Y-%m")

        orders = Order.objects.filter(
            created_at__year=date_obj.year,
            created_at__month=date_obj.month
        ).order_by('-created_at')

        if not orders.exists():
            return f"Không có đơn hàng tháng {month_str}"

        res = f"Đơn hàng tháng {month_str}:\n"

        for o in orders:

            status_vn = o.get_status_display()

            res += (
                f"- Mã đơn: {o.id}\n"
                f"  Trạng thái: {status_vn}\n"
                f"  Tổng giá: {o.total_price:,}₫\n"
            )

        res += f"\nTổng số đơn: {orders.count()}"

        return res

    except Exception as e:
        return f"Lỗi: {str(e)}"

def get_orders_by_year(year_str):
    """
    Lấy đơn hàng theo năm.
    Format: YYYY
    """
    try:
        year = int(year_str)

        orders = Order.objects.filter(
            created_at__year=year
        ).order_by('-created_at')

        if not orders.exists():
            return f"Không có đơn hàng năm {year}"

        res = f"Đơn hàng năm {year}:\n"

        for o in orders:

            status_vn = o.get_status_display()

            res += (
                f"- Mã đơn: {o.id}\n"
                f"  Trạng thái: {status_vn}\n"
                f"  Tổng giá: {o.total_price:,}₫\n"
            )

        res += f"\nTổng số đơn: {orders.count()}"

        return res

    except Exception as e:
        return f"Lỗi: {str(e)}"

# Lấy sản phẩm có lượt mua nhiều nhất
def get_product_sales_ranking(sort_order="desc"):
    """
    Lấy danh sách top sản phẩm có lượt mua nhiều nhất hoặc ít nhất.
    """
    try:
        products = Product.objects.annotate(
            total_sold=Coalesce(Sum('orderitem__quantity'), Value(0))
        )
        
        # Sắp xếp và lấy top 3
        if sort_order == "desc":
            products = products.order_by('-total_sold')[:3]
            res = "### Top 3 sản phẩm CÓ NHIỀU LƯỢT MUA NHẤT:\n"
        else:
            products = products.order_by('total_sold')[:3]
            res = "### Top 3 sản phẩm CÓ ÍT LƯỢT MUA NHẤT:\n"

        if not products.exists():
            return "Hiện tại cửa hàng chưa có sản phẩm nào."

        for p in products:
            res += f"- **{p.name}** (ID: {p.id}) | Đã bán: {p.total_sold} sản phẩm\n"
            
        return res
    except Exception as e:
        return f"Lỗi khi truy vấn thống kê: {str(e)}"

def search_product_knowledge(query):
    """Tìm kiếm thông tin chi tiết của sản phẩm từ cơ sở dữ liệu kiến thức (RAG)."""
    try:
        contexts = search_products(query)
        if not contexts:
            return "Không tìm thấy thông tin sản phẩm phù hợp trong hệ thống."
        
        # Nối các content tìm được thành 1 đoạn văn bản
        res = "Thông tin chi tiết tìm được từ hệ thống:\n"
        for c in contexts:
            res += f"- {c['content']}\n"
        return res
    except Exception as e:
        return f"Lỗi khi tìm kiếm kiến thức: {str(e)}"

def get_my_order_status(user, date_str=None):
    """Tra cứu trạng thái đơn hàng của user đang đăng nhập."""
    # Hàm này nhận thêm tham số user từ executor
    if not user.is_authenticated:
        return "Yêu cầu người dùng đăng nhập để tra cứu thông tin đơn hàng."

    orders = Order.objects.filter(user=user).order_by('-created_at')

    if date_str:
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            orders = orders.filter(created_at__date=date_obj)
        except ValueError:
            return "Định dạng ngày không hợp lệ. Hãy thử lại với định dạng YYYY-MM-DD."

    latest_order = orders.first()
    
    if latest_order:
        status_vi = latest_order.get_status_display()
        date_format = latest_order.created_at.strftime('%d/%m/%Y lúc %H:%M:%S')
        return f"Hệ thống ghi nhận: Đơn hàng mã {latest_order.id} đặt ngày {date_format}, trạng thái hiện tại là: {status_vi}."
    else:
        if date_str:
            return f"Không tìm thấy đơn hàng nào của bạn đặt vào ngày {date_str}."
        return "Không tìm thấy đơn hàng nào của bạn trong hệ thống."

def filter_products_by_price(min_price=None, max_price=None):
    """
    Dành cho USER: Tìm điện thoại theo mức giá hoặc khoảng giá.
    """
    try:
        products = Product.objects.all().select_related('brand')
        
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)
            
        # Sắp xếp từ rẻ đến đắt, lấy tối đa 10 máy
        products = products.order_by('price')[:10]
        
        if not products.exists():
            return "Rất tiếc, hệ thống không tìm thấy sản phẩm nào trong tầm giá này."
            
        res = f"Tìm thấy {products.count()} sản phẩm phù hợp:\n"
        for p in products:
            res += f"- {p.name} ({p.brand.name}) | Giá: {p.price:,}₫\n"
        
        res += "\nBạn cần xem chi tiết máy nào không?"
        return res
    except Exception as e:
        return f"Lỗi lọc giá: {str(e)}"

def admin_get_order_details(order_id):
    """
    DÀNH RIÊNG CHO ADMIN: Tra cứu chi tiết toàn bộ thông tin của một đơn hàng bất kỳ theo ID.
    """
    try:
        # Bước chuẩn hóa (Clean data): Loại bỏ dấu '#' và ép kiểu về số nguyên
        if isinstance(order_id, str):
            clean_id = order_id.replace("#", "").strip()
            order_id = int(clean_id)
            
        order = Order.objects.filter(id=order_id).select_related('user').first()
        if not order:
            return f"Không tìm thấy đơn hàng mã #{order_id} trên hệ thống."
        
        items = OrderItem.objects.filter(order=order).select_related('product')
        order_date = order.created_at.strftime("%d/%m/%Y %H:%M") if hasattr(order, 'created_at') else "Không rõ ngày đặt"

        res = f"### [BÁO CÁO ADMIN] CHI TIẾT ĐƠN HÀNG #{order.id}\n"
        res += f"- **Khách hàng đặt:** {order.user.name} (ID: {order.user.id} | Email: {order.user.email})\n"
        res += f"- **Ngày đặt hàng:** {order_date}\n"
        res += f"- **Trạng thái hiện tại:** {order.get_status_display() if hasattr(order, 'get_status_display') else order.status}\n"
        res += "---------------------------------------\n"
        res += "**Chi tiết các sản phẩm trong đơn:**\n"
        
        total_price = 0
        for item in items:
            line_total = item.price * item.quantity
            total_price += line_total
            res += f"• {item.product.name} | SL: {item.quantity} | Đơn giá: {item.price:,}₫ | Thành tiền: {line_total:,}₫\n"
            
        res += "---------------------------------------\n"
        res += f"**TỔNG DOANH THU ĐƠN HÀNG: {total_price:,}₫**"
        
        return res
    except ValueError:
        return f"Lỗi: Mã đơn hàng '{order_id}' không hợp lệ (phải là số nguyên)."
    except Exception as e:
        return f"Lỗi hệ thống khi admin tra cứu đơn hàng #{order_id}: {str(e)}"