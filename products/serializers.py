from rest_framework import serializers
from .models import Product, ProductSpec, ProductImage

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image_url']



class ProductSpecSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpec
        fields = [
            'screen',
            'cpu',
            'ram',
            'storage',
            'battery',
            'camera',
            'os'
        ]
        
class ProductSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name')
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_image(self, obj):
        img = ProductImage.objects.filter(product=obj).first()
        if img:
            # Tự động thêm đường dẫn static vào trước tên file
            # Để ảnh trong thư mục static/images/
            return f"/static/images/{img.image_url}" 
        return None

class ProductDetailSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name')
    specs = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_specs(self, obj):
        spec = ProductSpec.objects.filter(product=obj).first()
        return ProductSpecSerializer(spec).data if spec else None

    def get_images(self, obj):
        images = ProductImage.objects.filter(product=obj)
        data = ProductImageSerializer(images, many=True).data
        # Sửa đường dẫn cho từng ảnh trong danh sách chi tiết
        for item in data:
            if item['image_url']:
                item['image_url'] = f"/static/images/{item['image_url']}"
        return data



