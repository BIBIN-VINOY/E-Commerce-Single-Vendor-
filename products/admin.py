from django.contrib import admin
from . models import Category, Brand, Product, ProductImage ,ProductVariant,Review,Color

# Register your models here.

admin.site.register(Category)
admin.site.register(ProductVariant)
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Color)
admin.site.register(Review)