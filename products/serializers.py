from rest_framework import serializers

from .models import (
    Category,
    Brand,
    Product,
    ProductVariant,
    ProductImage,
    Color,
)


# -------------------------
# CATEGORY SERIALIZERS
# -------------------------

class CategoryBriefSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'slug',
        ]


class CategorySerializer(serializers.ModelSerializer):

    parent = CategoryBriefSerializer(read_only=True)
    subcategories = CategoryBriefSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'slug',
            'parent',
            'subcategories',
            'description',
            'image',
            'created_at',
        ]


# -------------------------
# BRAND SERIALIZERS
# -------------------------

class BrandSerializer(serializers.ModelSerializer):

    class Meta:
        model = Brand
        fields = [
            'id',
            'name',
            'slug',
            'logo',
            'description',
        ]


# -------------------------
# COLOR SERIALIZER
# -------------------------

class ColorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Color
        fields = [
            'id',
            'name',
            'hex_code',
        ]


# -------------------------
# PRODUCT IMAGE SERIALIZER
# -------------------------

class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage
        fields = [
            'id',
            'image',
            'is_primary',
        ]


# -------------------------
# PRODUCT VARIANT SERIALIZERS
# -------------------------

class ProductVariantListSerializer(serializers.ModelSerializer):

    color = ColorSerializer(read_only=True)

    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = [
            'id',
            'color',
            'price',
            'stock',
            'primary_image',
        ]

    def get_primary_image(self, obj):
        images = list(obj.images.all())

        primary = next(
            (image for image in images if image.is_primary),
            images[0] if images else None
        )

        if primary and primary.image:
            request = self.context.get('request')
            return request.build_absolute_uri(primary.image.url) if request else primary.image.url

        return None


class ProductVariantDetailSerializer(serializers.ModelSerializer):

    color = ColorSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = [
            'id',
            'color',
            'price',
            'stock',
            'is_default',
            'images',
            'primary_image',
        ]

    def get_primary_image(self, obj):
        images = list(obj.images.all())

        primary = next(
            (image for image in images if image.is_primary),
            images[0] if images else None
        )

        if primary and primary.image:
            request = self.context.get('request')
            return request.build_absolute_uri(primary.image.url) if request else primary.image.url

        return None


# -------------------------
# PRODUCT SERIALIZERS
# -------------------------

class ProductListSerializer(serializers.ModelSerializer):

    category = CategoryBriefSerializer(read_only=True)
    brand = BrandSerializer(read_only=True)

    variants = ProductVariantListSerializer(
        many=True,
        read_only=True
    )

    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'category',
            'brand',
            'price',
            'is_featured',
            'variants',
            'created_at',
        ]


class ProductDetailSerializer(serializers.ModelSerializer):

    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)

    variants = ProductVariantDetailSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'category',
            'brand',
            'status',
            'is_featured',
            'variants',
            'created_at',
            'updated_at',
        ]