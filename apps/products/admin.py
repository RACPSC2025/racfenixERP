from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ('image_thumbnail', 'product_name', 'product_sku', 'product_category', 'product_stock', 'product_price', 'is_active')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'sku', 'barcode')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    list_per_page = 20
    fieldsets = (
        ("Identificación", {
            "fields": ('name', 'sku', 'barcode', 'description', 'image_url', 'image_preview')
        }),
        ("Financiero", {
            "fields": ('price', 'cost')
        }),
        ("Inventario", {
            "fields": ('stock', 'min_stock', 'category', 'is_active')
        }),
        ("Fechas", {
            "fields": ('created_at', 'updated_at'),
            "classes": ('collapse',)
        }),
    )

    # --- Columnas personalizadas ---

    @admin.display(description="Imagen")
    def image_thumbnail(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="width:45px; height:45px; object-fit:cover; border-radius:8px; border:1px solid #e2e8f0;" />',
                obj.image_url
            )
        return format_html(
            '<div style="width:45px; height:45px; background:#f1f5f9; border-radius:8px; display:flex; align-items:center; justify-content:center; color:#94a3b8; font-size:18px;">📦</div>'
        )

    @admin.display(description="Product Name", ordering="name")
    def product_name(self, obj):
        return obj.name

    @admin.display(description="SKU", ordering="sku")
    def product_sku(self, obj):
        return format_html(
            '<code style="background:#f1f5f9; padding:2px 6px; border-radius:4px; font-size:12px; color:#6366f1;">{}</code>',
            str(obj.sku)[:12]
        )

    @admin.display(description="Category", ordering="category__name")
    def product_category(self, obj):
        if obj.category:
            return obj.category.name
        return "—"

    @admin.display(description="Stock", ordering="stock")
    def product_stock(self, obj):
        color = "#22c55e" if obj.stock > obj.min_stock else "#ef4444"
        return format_html(
            '<span style="font-weight:600; color:{};">{}</span>',
            color, obj.stock
        )

    @admin.display(description="Price", ordering="price")
    def product_price(self, obj):
        formatted = f"${obj.price:,.2f}"
        return format_html(
            '<span style="font-weight:600;">{}</span>',
            formatted
        )

    # --- Preview grande para el formulario de edición ---

    @admin.display(description="Vista previa")
    def image_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="max-width:200px; max-height:200px; object-fit:contain; border-radius:12px; border:1px solid #e2e8f0;" />',
                obj.image_url
            )
        return "Sin imagen"
