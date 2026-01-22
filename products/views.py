from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import render, get_object_or_404
from .models import Product, ProductSpec, ProductImage
from .serializers import ProductSerializer, ProductDetailSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import FileSystemStorage
from products.models import Product, ProductImage, Brand, ProductSpec

from django.utils import timezone

# --- API VIEWS (JSON) ---

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductListAPI(APIView):
    def get(self, request):
        # Lấy tham số tìm kiếm và lọc hãng từ URL (nếu có)
        search_query = request.GET.get('search', '')
        brand_query = request.GET.get('brand', '')

        # Query gốc
        products = Product.objects.all().order_by('-id')

        # Xử lý lọc dữ liệu (Server-side filtering)
        if search_query:
            products = products.filter(name__icontains=search_query)
        if brand_query and brand_query != "-- Tất cả hãng --":
            products = products.filter(brand__name=brand_query)

        # Áp dụng phân trang
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(products, request)
        
        serializer = ProductSerializer(result_page, many=True)
        
        # Trả về kết quả kèm thông tin phân trang (count, next, previous, results)
        return paginator.get_paginated_response(serializer.data)

class ProductDetailAPI(APIView):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        return Response(ProductDetailSerializer(product).data)
    
class HomeProductAPI(APIView):
    def get(self, request):
        products = Product.objects.order_by('-id')[:5]
        return Response(ProductSerializer(products, many=True).data)
    #.data -> trả về dạng dictionary

# ADMIN
# 1. API LẤY DANH SÁCH & TẠO MỚI
class AdminProductListView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request):
        if getattr(request.user, 'role', '') != 'admin': 
            return Response({"error": "Forbidden"}, status=403)
        
        products = Product.objects.all().order_by('-id')
        
        # Áp dụng phân trang 10 sản phẩm/trang từ class StandardResultsSetPagination
        paginator = StandardResultsSetPagination() 
        result_page = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(result_page, many=True)
        
        # Trả về dữ liệu có cấu trúc: { count, next, previous, results }
        return paginator.get_paginated_response(serializer.data)

    # Tạo mới sản phẩm (POST)
    def post(self, request):
        if getattr(request.user, 'role', '') != 'admin': 
            return Response({"error": "Forbidden"}, status=403)
        
        try:
            data = request.data
            
            # 1. Tạo Product
            brand_id = data.get('brand')
            brand_obj = None
            if brand_id:
                brand_obj = Brand.objects.filter(id=brand_id).first()

            new_p = Product.objects.create(
                name=data.get('name'),
                price=data.get('price'),
                description=data.get('description'),
                brand=brand_obj,
                created_at=timezone.now()
            )

            # 2. Tạo ProductSpec (Thông số kỹ thuật)
            ProductSpec.objects.create(
                product=new_p,
                screen=data.get('screen', ''),
                cpu=data.get('cpu', ''),
                ram=data.get('ram', ''),
                storage=data.get('storage', ''),
                battery=data.get('battery', ''),
                camera=data.get('camera', ''),
                os=data.get('os', '')
            )

            # 3. Lưu ảnh (ProductImage)
            image_file = request.FILES.get('image')
            if image_file:
                fs = FileSystemStorage(location='static/images')
                filename = fs.save(image_file.name, image_file)
                ProductImage.objects.create(product=new_p, image_url=filename)

            return Response({"message": "Tạo thành công", "id": new_p.id}, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class AdminProductDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    # Lấy chi tiết sản phẩm để hiển thị lên form sửa (GET)
    def get(self, request, pk):
        if getattr(request.user, 'role', '') != 'admin': 
            return Response({"error": "Forbidden"}, status=403)
            
        p = get_object_or_404(Product, pk=pk)
        
        # Lấy ảnh
        first_img = ProductImage.objects.filter(product=p).first()
        img_url = f"/static/images/{first_img.image_url}" if first_img else ""

        # Lấy thông số kỹ thuật
        spec_data = {}
        spec = ProductSpec.objects.filter(product=p).first()
        if spec:
            spec_data = {
                "screen": spec.screen,
                "cpu": spec.cpu,
                "ram": spec.ram,
                "storage": spec.storage,
                "battery": spec.battery,
                "camera": spec.camera,
                "os": spec.os
            }

        data = {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "description": p.description,
            "brand": p.brand.id if p.brand else "",
            "thumbnail": img_url,
            "specs": spec_data  
        }
        return Response(data)

    # Cập nhật sản phẩm (PUT)
    def put(self, request, pk):
        if getattr(request.user, 'role', '') != 'admin': 
            return Response({"error": "Forbidden"}, status=403)
        
        try:
            p = get_object_or_404(Product, pk=pk)
            data = request.data
            
            # 1. Update Product
            p.name = data.get('name', p.name)
            p.price = data.get('price', p.price)
            p.description = data.get('description', p.description)
            
            brand_id = data.get('brand')
            if brand_id and str(brand_id).strip():
                brand_obj = Brand.objects.filter(id=brand_id).first()
                if brand_obj: p.brand = brand_obj
            p.save()

            # 2. Update Spec
            spec_defaults = {
                "screen": data.get('screen', ''),
                "cpu": data.get('cpu', ''),
                "ram": data.get('ram', ''),
                "storage": data.get('storage', ''),
                "battery": data.get('battery', ''),
                "camera": data.get('camera', ''),
                "os": data.get('os', '')
            }
            # update_or_create: nếu chưa có thì tạo mới, có rồi thì update
            ProductSpec.objects.update_or_create(product=p, defaults=spec_defaults)
            
            # 3. Update Image
            image_file = request.FILES.get('image')
            if image_file:
                ProductImage.objects.filter(product=p).delete() # Xóa ảnh cũ
                fs = FileSystemStorage(location='static/images')
                filename = fs.save(image_file.name, image_file)
                ProductImage.objects.create(product=p, image_url=filename)

            return Response({"message": "Cập nhật thành công!"})
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    # Xóa sản phẩm (DELETE)
    def delete(self, request, pk):
        if getattr(request.user, 'role', '') != 'admin': 
            return Response({"error": "Forbidden"}, status=403)
        p = get_object_or_404(Product, pk=pk)
        ProductImage.objects.filter(product=p).delete()
        p.delete()
        return Response(status=204)

class BrandListAPI(APIView):
    """API trả về danh sách tất cả các hãng để hiển thị lên dropdown"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        brands = Brand.objects.all()
        data = [{"id": b.id, "name": b.name} for b in brands]
        return Response(data)

# --- FRONTEND VIEWS (HTML) ---

def product_list_page(request):
    """Render trang danh sách sản phẩm"""
    return render(request, 'products/product_list.html')

def product_detail_page(request, pk):
    """Render trang chi tiết sản phẩm (truyền ID vào template để JS dùng)"""
    return render(request, 'products/product_detail.html', {'product_id': pk})

def admin_product_page(request):
    """Render trang Admin quản lý sản phẩm"""
    return render(request, 'admin/products.html')