from django.db import models

class Brand(models.Model):
    name = models.CharField(max_length=255)
    # Các trường khác nếu cần (dựa theo ảnh: id serial, name text)
    
    class Meta:
        db_table = 'brands' 
        managed = False      

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.BigIntegerField()
    description = models.TextField()
    # Khóa ngoại trỏ về bảng brands, cột brand_id
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, db_column='brand_id')
    
    class Meta:
        db_table = 'products'  
        managed = False       