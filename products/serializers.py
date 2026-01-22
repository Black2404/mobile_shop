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

            return f"/static/images/{img.image_url}" 
        return None
    def get_brand_name(self, obj):
        if obj.brand:
            return obj.brand.name
        return "Chưa cập nhật"

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
class ProductWriteSerializer(serializers.ModelSerializer):
    # Khi thêm/sửa, ta gửi brand_id thay vì brand_name
    brand_id = serializers.IntegerField() 
    
    # Nhận dữ liệu specs và images từ client gửi lên dưới dạng JSON
    specs = serializers.DictField(write_only=True, required=False)
    images = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description', 'brand_id', 'specs', 'images']

    def create(self, validated_data):
        # Tách dữ liệu specs và images ra khỏi product
        specs_data = validated_data.pop('specs', None)
        images_data = validated_data.pop('images', [])
        
        # 1. Tạo Product
        product = Product.objects.create(**validated_data)
        
        # 2. Tạo ProductSpec (nếu có)
        if specs_data:
            ProductSpec.objects.create(product=product, **specs_data)
            
        # 3. Tạo ProductImage (nếu có)
        # images_data là danh sách url: ["img1.jpg", "img2.jpg"]
        for img_url in images_data:
            ProductImage.objects.create(product=product, image_url=img_url)
            
        return product

    def update(self, instance, validated_data):
        specs_data = validated_data.pop('specs', None)
        images_data = validated_data.pop('images', None)

        # 1. Cập nhật thông tin cơ bản Product
        instance.name = validated_data.get('name', instance.name)
        instance.price = validated_data.get('price', instance.price)
        instance.description = validated_data.get('description', instance.description)
        instance.brand_id = validated_data.get('brand_id', instance.brand_id)
        instance.save()

        # 2. Cập nhật Specs (Xóa cũ tạo mới hoặc update - ở đây chọn cách update nếu tồn tại)
        if specs_data:
            spec_instance, created = ProductSpec.objects.get_or_create(product=instance)
            for attr, value in specs_data.items():
                setattr(spec_instance, attr, value)
            spec_instance.save()

        # 3. Cập nhật Images (Chiến lược: Xóa hết ảnh cũ, thêm ảnh mới - đơn giản nhất)
        if images_data is not None:
            ProductImage.objects.filter(product=instance).delete()
            for img_url in images_data:
                ProductImage.objects.create(product=instance, image_url=img_url)

        return instance


