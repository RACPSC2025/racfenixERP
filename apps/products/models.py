import uuid
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre de la Categoría")
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    # 1. Identificación
    name = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    sku = models.CharField(max_length=50, unique=True, db_index=True, default=uuid.uuid4, verbose_name="SKU / Código Interno")
    barcode = models.CharField(max_length=100, blank=True, null=True, verbose_name="Código de Barras")
    description = models.TextField(blank=True, verbose_name="Descripción")
    image_url = models.URLField(max_length=1000, blank=True, null=True, verbose_name="URL de Imagen")
    
    # 2. Financiero
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio de Venta")
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo de Compra")
    
    # 3. Inventario
    stock = models.IntegerField(default=0, verbose_name="Stock Actual")
    min_stock = models.IntegerField(default=5, verbose_name="Stock Mínimo")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    # 4. Relaciones
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name="Categoría")
    
    # 5. Fechas auditoría
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado el")

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['name']

    def __str__(self):
        return f"[{str(self.sku)[:8]}] {self.name}"
