from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from .models import Product
from .serializers import ProductSerializer, ProductDetailSerializer

# --- API VIEWS (JSON) ---

class ProductListAPI(APIView):
    def get(self, request):
        products = Product.objects.all()
        return Response(ProductSerializer(products, many=True).data)

class ProductDetailAPI(APIView):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        return Response(ProductDetailSerializer(product).data)
    
class HomeProductAPI(APIView):
    def get(self, request):
        products = Product.objects.order_by('-id')[:5]
        return Response(ProductSerializer(products, many=True).data)

# --- FRONTEND VIEWS (HTML) ---

def product_list_page(request):
    """Render trang danh sách sản phẩm"""
    return render(request, 'products/product_list.html')

def product_detail_page(request, pk):
    """Render trang chi tiết sản phẩm (truyền ID vào template để JS dùng)"""
    return render(request, 'products/product_detail.html', {'product_id': pk})