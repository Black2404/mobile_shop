from django.db import models

class Brand(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()

    class Meta:
        managed = False
        db_table = 'brands'


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    brand = models.ForeignKey(Brand, on_delete=models.DO_NOTHING, db_column='brand_id')
    name = models.TextField()
    price = models.BigIntegerField()
    description = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'products'


class ProductSpec(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.OneToOneField(Product, on_delete=models.DO_NOTHING, db_column='product_id')
    screen = models.TextField()
    cpu = models.TextField()
    ram = models.TextField()
    storage = models.TextField()
    battery = models.TextField()
    camera = models.TextField()
    os = models.TextField()

    class Meta:
        managed = False
        db_table = 'product_specs'


class ProductImage(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, db_column='product_id')
    image_url = models.TextField()

    class Meta:
        managed = False
        db_table = 'product_images'
