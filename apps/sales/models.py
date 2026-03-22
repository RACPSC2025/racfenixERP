# =============================================================================
# apps/sales/models.py
# =============================================================================
# MODELOS DEL MÓDULO DE VENTAS
# Este archivo contiene todos los modelos relacionados con el proceso de ventas:
# - SalesOrder: Orden de venta principal
# - SalesOrderItem: Detalle de productos en cada orden
# - Payment: Registro de pagos
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS NECESARIOS
# ─────────────────────────────────────────────────────────────────────────────

# models: Para definir campos y modelos de Django
from django.db import models

# settings: Para acceder a configuraciones globales como AUTH_USER_MODEL
from django.conf import settings

# Decimal: Para manejo preciso de dinero (NUNCA usar float para dinero)
from decimal import Decimal

# HistoricalRecords: Para auditoría automática de cambios (django-simple-history)
from simple_history.models import HistoricalRecords

# timezone: Para manejo correcto de fechas y horas
from django.utils import timezone

# ValidationError: Para validaciones personalizadas en el método clean()
from django.core.exceptions import ValidationError

# NOTA: NO necesitamos importar Product ni Customer aquí porque usamos
# referencias por string ('products.Product', 'customers.Customer')
# Esto evita imports circulares y acoplamiento innecesario


# ─────────────────────────────────────────────────────────────────────────────
# CLASES DE CHOICES (CONSTANTES TIPO ENUM)
# ─────────────────────────────────────────────────────────────────────────────
# TextChoices es la forma moderna de Django de definir opciones para campos
# Es mejor que usar tuplas porque es más legible y type-safe

class OrderStatus(models.TextChoices):
    """
    Estados posibles de una orden de venta.
    Usamos TextChoices para tener autocompletado y validación en el código.
    """
    # Formato: VALOR_INTERNO = 'clave_en_bd', 'Nombre para mostrar'
    PENDING = 'pending', 'Pendiente'
    CONFIRMED = 'confirmed', 'Confirmada'
    PAID = 'paid', 'Pagada'
    PENDING_DELIVERY = 'pending_delivery', 'Por Entregar'
    COMPLETED = 'completed', 'Completada'
    CANCELLED = 'cancelled', 'Cancelada'


class PaymentMethod(models.TextChoices):
    """
    Métodos de pago aceptados por el sistema.
    Puedes agregar más según tu negocio (Yape, Plin, etc.)
    """
    CASH = 'cash', 'Efectivo'
    CREDIT_CARD = 'credit_card', 'Tarjeta de Crédito'
    DEBIT_CARD = 'debit_card', 'Tarjeta de Débito'
    BANK_TRANSFER = 'bank_transfer', 'Transferencia Bancaria'
    YAPE = 'yape', 'Yape'
    PLIN = 'plin', 'Plin'


# ─────────────────────────────────────────────────────────────────────────────
# MODELO PRINCIPAL: SALES ORDER (ORDEN DE VENTA)
# ─────────────────────────────────────────────────────────────────────────────
class SalesOrder(models.Model):
    """
    Representa una orden de venta completa.
    Es el documento principal que registra una venta a un cliente.
    Contiene información del cliente, vendedor, estado, fechas y totales.
    
    Relación con otros modelos:
    - Customer: N:1 (Un cliente tiene muchas órdenes)
    - User (sales_rep): N:1 (Un vendedor tiene muchas órdenes)
    - SalesOrderItem: 1:N (Una orden tiene muchos detalles/items)
    - Payment: 1:N (Una orden puede tener múltiples pagos)
    """
    
    # =========================================================================
    # 1. CAMPOS DE IDENTIFICACIÓN
    # =========================================================================
    
    # order_number: Número único de la orden
    # - max_length=20: Suficiente para formato SO-YYYYMMDD-0001
    # - unique=True: No pueden existir dos órdenes con mismo número
    # - editable=False: No se puede editar manualmente (se genera automático)
    order_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name='Número de Orden'
    )
    
    # =========================================================================
    # 2. CAMPOS DE RELACIÓN (FOREIGN KEYS)
    # =========================================================================
    
    # customer: Cliente que realiza la compra
    # - 'customers.Customer': Referencia por string a app externa
    # - on_delete=models.PROTECT: No se puede eliminar cliente si tiene ventas
    # - related_name='sales_orders': Para acceder desde cliente (cliente.sales_orders.all())
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.PROTECT,
        related_name='sales_orders',
        verbose_name='Cliente'
    )
    
    # sales_rep: Vendedor/representante que atendió la venta
    # - settings.AUTH_USER_MODEL: Referencia al modelo custom de usuario
    # - null=True, blank=True: Puede ser nulo (ventas sin vendedor asignado)
    sales_rep = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='sales_orders',
        verbose_name='Representante de Ventas'
    )
    
    # =========================================================================
    # 3. CAMPOS DE ESTADO
    # =========================================================================
    
    # status: Estado actual de la orden
    # - choices=OrderStatus.choices: Solo permite valores del TextChoices
    # - default=OrderStatus.PENDING: Nueva orden comienza como pendiente
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        verbose_name='Estado'
    )
    
    # =========================================================================
    # 4. CAMPOS DE FECHA
    # =========================================================================
    
    # created_at: Fecha y hora de creación del registro
    # - auto_now_add=True: Se establece automáticamente al crear (solo lectura)
    # - DateTimeField: Incluye fecha Y hora (más preciso que DateField)
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    # updated_at: Fecha y hora de última modificación
    # - auto_now=True: Se actualiza automáticamente en cada save()
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )
    
    # sale_date: Fecha específica de la venta (puede diferir de created_at)
    # - default=timezone.now: Por defecto es la fecha/hora actual
    # - Permite registrar ventas con fecha retroactiva si es necesario
    sale_date = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Venta'
    )
    
    # =========================================================================
    # 5. CAMPOS MONETARIOS (TOTALES)
    # =========================================================================
    # NOTA: Usamos DecimalField para dinero (NUNCA FloatField)
    # - max_digits=12: Máximo 12 dígitos en total (ej: 999,999,999.99)
    # - decimal_places=2: Siempre 2 decimales para centavos
    # - default=Decimal('0.00'): Valor inicial para evitar errores
    
    # subtotal: Suma de todos los items ANTES de impuestos y descuentos
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Subtotal'
    )
    
    # tax_rate: Porcentaje de impuesto (ej: 18% IGV en Perú)
    # - max_digits=5: Suficiente para porcentajes (ej: 999.99%)
    # - decimal_places=2: Permite decimales en el porcentaje
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('18.00'),
        verbose_name='Tasa de Impuesto (%)'
    )
    
    # tax_amount: Monto calculado del impuesto
    # - editable=False: No se edita manualmente, se calcula automático
    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        verbose_name='Monto de Impuesto'
    )
    
    # total_amount: Total final a pagar (subtotal + impuesto - descuento)
    # - Este es el monto que el cliente debe pagar
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        verbose_name='Total a Pagar'
    )
    
    # =========================================================================
    # 6. CAMPOS DE DESCUENTO
    # =========================================================================
    
    # discount_rate: Porcentaje de descuento (opcional)
    discount_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Tasa de Descuento (%)'
    )
    
    # discount_amount: Monto fijo de descuento (en moneda)
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Monto de Descuento'
    )
    
    # =========================================================================
    # 7. CAMPOS DE INFORMACIÓN ADICIONAL
    # =========================================================================
    
    # notes: Observaciones o comentarios adicionales
    # - blank=True: Campo opcional (puede estar vacío)
    # - TextField: Permite texto largo (ilimitado prácticamente)
    notes = models.TextField(
        blank=True,
        verbose_name='Observaciones'
    )
    
    # =========================================================================
    # 8. AUDITORÍA (HISTORIAL DE CAMBIOS)
    # =========================================================================
    
    # history: Historial automático de cambios con django-simple-history
    # - Crea una tabla histórica paralela (sales_historicalsalesorder)
    # - Registra: quién cambió, cuándo, qué valores antes/después
    # - NO necesitamos campos history_* adicionales (ya los incluye automático)
    history = HistoricalRecords()
    
    # NOTA: Eliminamos history_created_at, history_updated_at, history_user
    # porque simple_history ya los crea automáticamente en la tabla histórica.
    # Tenerlos aquí sería duplicar información y causar confusión.
    
    # =========================================================================
    # 9. META CLASE (CONFIGURACIÓN DEL MODELO)
    # =========================================================================
    # La clase Meta contiene opciones de configuración que no son campos
    
    class Meta:
        """
        Configuración del modelo SalesOrder.
        Define cómo se comporta el modelo en Django Admin y en la BD.
        """
        
        # verbose_name: Nombre singular para Django Admin
        verbose_name = 'Orden de Venta'
        
        # verbose_name_plural: Nombre plural para Django Admin
        verbose_name_plural = 'Órdenes de Venta'
        
        # ordering: Orden por defecto al consultar objetos
        # - ['-created_at']: Más recientes primero (el - indica descendente)
        # - Sin coma al final: Debe ser una lista, no una tupla de lista
        ordering = ['-created_at']
        
        # indexes: Índices de base de datos para optimizar consultas
        # - Los índices aceleran las búsquedas en campos frecuentes
        indexes = [
            # Búsqueda por número de orden (muy común)
            models.Index(fields=['order_number']),
            # Órdenes de un cliente específico, ordenadas por fecha
            models.Index(fields=['customer', '-created_at']),
            # Órdenes de un vendedor específico, ordenadas por fecha
            models.Index(fields=['sales_rep', '-created_at']),
            # Órdenes filtradas por estado, ordenadas por fecha
            models.Index(fields=['status', '-created_at']),
        ]
        
        # constraints: Restricciones de integridad de la base de datos
        # - Validaciones a nivel de BD (más estrictas que validaciones de Django)
        # NOTA: En Django 5.2 LTS se usa 'check=' (no 'condition=')
        constraints = [
            # El total debe ser mayor o igual a 0 (no puede ser negativo)
            models.CheckConstraint(
                check=models.Q(total_amount__gte=0),
                name='sales_order_total_amount_non_negative'
            ),
            # El subtotal debe ser mayor o igual a 0
            models.CheckConstraint(
                check=models.Q(subtotal__gte=0),
                name='sales_order_subtotal_non_negative'
            ),
        ]
    
    # =========================================================================
    # 10. MÉTODO __str__ (REPRESENTACIÓN EN TEXTO)
    # =========================================================================
    
    def __str__(self):
        """
        Representación legible del objeto como string.
        Se muestra en el Admin de Django y en print().
        """
        # Formato: "Orden SO-20260322-0001 - Cliente S.A.C."
        return f"Orden {self.order_number} - {self.customer}"
    
    # =========================================================================
    # 11. MÉTODO save() (GUARDADO PERSONALIZADO)
    # =========================================================================
    
    def save(self, *args, **kwargs):
        """
        Sobreescribe el método save() para:
        1. Generar automáticamente el order_number si es nuevo
        2. Llamar al save() original de Django
        3. Recalcular totales después de guardar
        
        *args, **kwargs: Acepta argumentos variables para compatibilidad
        """
        
        # Si es una orden nueva (sin order_number), generarlo automáticamente
        if not self.order_number:
            # Obtener fecha actual en formato YYYYMMDD
            # Ej: 2026-03-22 → '20260322'
            today = timezone.now().strftime('%Y%m%d')
            
            # Buscar la última orden creada hoy
            # - order_number__startswith='SO-20260322': Filtra por fecha
            # - order_by('-order_number'): Ordena descendente (más reciente primero)
            # - .first(): Obtiene el primer resultado (el más reciente)
            last_order = (
                SalesOrder.objects
                .filter(order_number__startswith=f'SO-{today}')
                .order_by('-order_number')
                .first()
            )
            
            # Si existe una orden previa, extraer el correlativo y sumar 1
            if last_order:
                # Ej: 'SO-20260322-0001' → split('-') → ['SO', '20260322', '0001']
                # Índices:              [0]     [1]         [2]
                # Nos interesa [2] que es el correlativo '0001'
                last_seq = int(last_order.order_number.split('-')[2])
                new_seq = last_seq + 1  # Sumar 1 al correlativo
            else:
                # Si no hay órdenes previas, comenzar desde 1
                new_seq = 1
            
            # Formatear número con 4 dígitos (padding con ceros)
            # :04d significa: entero decimal con 4 dígitos, rellenar con ceros
            # Ej: 1 → '0001', 15 → '0015', 123 → '0123'
            self.order_number = f'SO-{today}-{new_seq:04d}'
        
        # Llamar al método save() original de Django
        # Esto guarda el objeto en la base de datos
        super().save(*args, **kwargs)
        
        # Recalcular totales después de guardar
        # Esto asegura que subtotal, tax_amount y total_amount estén actualizados
        self.calculate_totals()
    
    # =========================================================================
    # 12. MÉTODO calculate_totals() (CÁLCULO AUTOMÁTICO DE TOTALES)
    # =========================================================================
    
    def calculate_totals(self):
        """
        Calcula automáticamente subtotal, impuesto y total a partir de los items.
        Este método se llama automáticamente al guardar la orden o sus items.
        
        Proceso:
        1. Suma el total de todos los items (SalesOrderItem)
        2. Resta el descuento
        3. Calcula el impuesto basado en tax_rate
        4. Actualiza los campos en la base de datos
        """
        
        # Obtener todos los items de esta orden
        # - self.items.all(): Usa el related_name definido en SalesOrderItem
        items = self.items.all()
        
        # Calcular suma bruta de todos los items
        # - item.total_price: Precio total de cada línea (cantidad × precio unitario)
        raw_subtotal = sum(item.total_price for item in items)
        
        # Convertir a Decimal para precisión monetaria
        # - quantize(Decimal('0.01')): Redondea a 2 decimales
        subtotal = Decimal(str(raw_subtotal)).quantize(Decimal('0.01'))
        
        # Obtener monto de descuento (o 0 si es None)
        discount = Decimal(str(self.discount_amount or 0)).quantize(Decimal('0.01'))
        
        # Calcular tasa de impuesto como decimal
        # - Ej: 18% → Decimal('18.00') / Decimal('100') = 0.18
        tax_rate_decimal = Decimal(str(self.tax_rate)) / Decimal('100')
        
        # Calcular subtotal final (después de descuento)
        self.subtotal = (subtotal - discount).quantize(Decimal('0.01'))
        
        # Calcular monto de impuesto
        self.tax_amount = (self.subtotal * tax_rate_decimal).quantize(Decimal('0.01'))
        
        # Calcular total final (subtotal + impuesto)
        self.total_amount = (self.subtotal + self.tax_amount).quantize(Decimal('0.01'))
        
        # Actualizar directamente en la base de datos
        # - Usamos .update() para evitar llamar a save() recursivamente
        # - Si llamáramos a save() aquí, entraría en loop infinito
        SalesOrder.objects.filter(pk=self.pk).update(
            subtotal=self.subtotal,
            tax_amount=self.tax_amount,
            total_amount=self.total_amount
        )
    
    # =========================================================================
    # 13. PROPIEDADES (ATTRIBUTOS CALCULADOS)
    # =========================================================================
    # Las propiedades son métodos que se acceden como atributos (sin paréntesis)
    
    @property
    def total_items(self):
        """
        Cantidad total de items (líneas de producto) en la orden.
        Ej: Si la orden tiene 3 productos diferentes, retorna 3.
        """
        # .count() es más eficiente que len() porque hace COUNT(*) en SQL
        return self.items.count()
    
    @property
    def is_paid(self):
        """
        Verifica si la orden está completamente pagada.
        Retorna True si el estado es PAID, False en otro caso.
        """
        # Comparamos con OrderStatus.PAID (sin self. porque es clase de módulo)
        return self.status == OrderStatus.PAID
    
    @property
    def pending_amount(self):
        """
        Calcula el monto pendiente de pago.
        Si es 0, la orden está completamente pagada.
        """
        # Sumar todos los pagos registrados
        # - self.payments.all(): Usa related_name definido en Payment
        paid = sum(payment.amount for payment in self.payments.all())
        
        # Restar lo pagado del total
        return self.total_amount - paid


# ─────────────────────────────────────────────────────────────────────────────
# MODELO: SALES ORDER ITEM (DETALLE DE LA VENTA)
# ─────────────────────────────────────────────────────────────────────────────
class SalesOrderItem(models.Model):
    """
    Representa cada línea/producto dentro de una orden de venta.
    Una orden puede tener múltiples items (1:N).
    
    Ejemplo:
    Orden SO-001:
      - Item 1: 2x Laptop @ $1000 = $2000
      - Item 2: 5x Mouse @ $20 = $100
      - Item 3: 3x Teclado @ $50 = $150
    
    Relación con otros modelos:
    - SalesOrder: N:1 (Muchos items pertenecen a una orden)
    - Product: N:1 (Cada item es un producto específico)
    """
    
    # =========================================================================
    # 1. CAMPOS DE RELACIÓN
    # =========================================================================
    
    # order: Orden de venta a la que pertenece este item
    # - on_delete=models.CASCADE: Si se elimina la orden, se eliminan todos sus items
    # - related_name='items': Para acceder desde orden (orden.items.all())
    order = models.ForeignKey(
        SalesOrder,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Orden'
    )
    
    # product: Producto que se está vendiendo
    # - 'products.Product': Referencia por string a app externa
    # - on_delete=models.PROTECT: No se puede eliminar producto si tiene ventas
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='sales_items',
        verbose_name='Producto'
    )
    
    # =========================================================================
    # 2. CAMPOS DE CANTIDAD Y PRECIO
    # =========================================================================
    
    # quantity: Cantidad de unidades del producto
    # - PositiveIntegerField: Solo permite enteros positivos (0, 1, 2, ...)
    # - default=1: Por defecto 1 unidad
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Cantidad'
    )
    
    # unit_price: Precio unitario del producto
    # - Se copia del producto al momento de la venta (no cambia si cambia el producto)
    # - Esto preserva el histórico: el precio de venta queda registrado
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Precio Unitario'
    )
    
    # total_price: Precio total de esta línea (quantity × unit_price)
    # - editable=False: Se calcula automáticamente, no se edita manualmente
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
        verbose_name='Total Línea'
    )
    
    # =========================================================================
    # 3. AUDITORÍA
    # =========================================================================
    
    # history: Historial de cambios de este item
    # - Registra cambios en cantidad, precio, etc.
    history = HistoricalRecords()
    
    # =========================================================================
    # 4. META CLASE (CONFIGURACIÓN)
    # =========================================================================
    
    class Meta:
        """Configuración del modelo SalesOrderItem."""

        # Nombres para Django Admin
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Venta'

        # Constraints: Restricciones de integridad
        # NOTA: En Django 5.2 LTS se usa 'check=' (no 'condition=')
        constraints = [
            # La cantidad debe ser mayor a 0
            models.CheckConstraint(
                check=models.Q(quantity__gt=0),
                name='sales_order_item_quantity_positive'
            ),
            # El precio unitario debe ser mayor o igual a 0
            models.CheckConstraint(
                check=models.Q(unit_price__gte=0),
                name='sales_order_item_unit_price_non_negative'
            ),
        ]
    
    # =========================================================================
    # 5. MÉTODO __str__
    # =========================================================================
    
    def __str__(self):
        """Representación legible del item."""
        # Formato: "2x Laptop HP @ $1000.00"
        return f"{self.quantity}x {self.product.name} @ ${self.unit_price}"
    
    # =========================================================================
    # 6. MÉTODO save() (GUARDADO CON CÁLCULO AUTOMÁTICO)
    # =========================================================================
    
    def save(self, *args, **kwargs):
        """
        Sobreescribe save() para:
        1. Calcular automáticamente total_price (quantity × unit_price)
        2. Guardar el item
        3. Recalcular totales de la orden padre
        """
        
        # Calcular precio total de la línea
        # - Convertimos quantity a Decimal para precisión
        # - Ej: 2 × $1000.00 = $2000.00
        self.total_price = Decimal(str(self.quantity)) * self.unit_price
        
        # Llamar al save() original de Django
        super().save(*args, **kwargs)
        
        # Recalcular totales de la orden padre
        # - Esto actualiza subtotal, tax_amount y total_amount de la orden
        self.order.calculate_totals()
    
    # =========================================================================
    # 7. MÉTODO clean() (VALIDACIONES PERSONALIZADAS)
    # =========================================================================
    
    def clean(self):
        """
        Validaciones personalizadas que se ejecutan antes de guardar.
        Se llama automáticamente en formularios y admin.
        """
        
        # Validar que haya stock suficiente del producto
        if self.quantity > self.product.stock:
            # Si no hay stock, lanzar error de validación
            raise ValidationError({
                'quantity': f'Stock insuficiente. Disponible: {self.product.stock} unidades.'
            })


# ─────────────────────────────────────────────────────────────────────────────
# MODELO: PAYMENT (PAGO)
# ─────────────────────────────────────────────────────────────────────────────
class Payment(models.Model):
    """
    Representa un pago registrado para una orden de venta.
    Permite pagos parciales o completos.
    
    Ejemplo:
    Orden SO-001 con total $1000:
      - Pago 1: $500 (Efectivo) - 2026-03-22
      - Pago 2: $500 (Transferencia) - 2026-03-25
      → Orden queda como PAGADA
    
    Relación con otros modelos:
    - SalesOrder: N:1 (Muchos pagos pueden pertenecer a una orden)
    """
    
    # =========================================================================
    # 1. CAMPOS DE RELACIÓN
    # =========================================================================
    
    # order: Orden de venta a la que pertenece este pago
    # - on_delete=models.CASCADE: Si se elimina la orden, se eliminan sus pagos
    # - related_name='payments': Para acceder desde orden (orden.payments.all())
    order = models.ForeignKey(
        SalesOrder,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Orden'
    )
    
    # =========================================================================
    # 2. CAMPOS DEL PAGO
    # =========================================================================
    
    # payment_method: Método de pago utilizado
    # - choices=PaymentMethod.choices: Solo permite valores definidos
    # - default=PaymentMethod.CASH: Por defecto efectivo
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH,
        verbose_name='Método de Pago'
    )
    
    # amount: Monto del pago
    # - Debe ser mayor a 0 (validado por constraint)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Monto'
    )
    
    # payment_date: Fecha y hora del pago
    # - auto_now_add=True: Se establece automáticamente al crear
    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Pago'
    )
    
    # reference: Número de referencia o comprobante
    # - blank=True: Opcional (no todos los pagos tienen referencia)
    # - Útil para transferencias (número de operación), cheques, etc.
    reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Referencia/Nro. Operación'
    )
    
    # notes: Observaciones adicionales sobre el pago
    notes = models.TextField(
        blank=True,
        verbose_name='Observaciones'
    )
    
    # =========================================================================
    # 3. AUDITORÍA
    # =========================================================================
    
    # history: Historial de cambios del pago
    history = HistoricalRecords()
    
    # NOTA: Eliminamos created_at porque ya tenemos payment_date
    # Tener ambos sería duplicar información innecesariamente
    
    # =========================================================================
    # 4. META CLASE (CONFIGURACIÓN)
    # =========================================================================
    
    class Meta:
        """Configuración del modelo Payment."""
        
        # Nombres para Django Admin
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        
        # Orden por defecto: más recientes primero
        ordering = ['-payment_date']
        
        # Índices para optimizar consultas frecuentes
        indexes = [
            # Pagos de una orden específica, ordenados por fecha
            models.Index(fields=['order', '-payment_date']),
            # Pagos filtrados por método, ordenados por fecha
            models.Index(fields=['payment_method', '-payment_date']),
        ]
        
        # Constraints: Restricciones de integridad
        # NOTA: En Django 5.2 LTS se usa 'check=' (no 'condition=')
        constraints = [
            # El monto debe ser mayor a 0 (no puede ser 0 o negativo)
            models.CheckConstraint(
                check=models.Q(amount__gt=0),
                name='payment_amount_positive'
            ),
        ]
    
    # =========================================================================
    # 5. MÉTODO __str__
    # =========================================================================
    
    def __str__(self):
        """Representación legible del pago."""
        # Formato: "Pago $500.00 - Efectivo - 22/03/2026"
        return (
            f"Pago ${self.amount} - "
            f"{self.get_payment_method_display()} - "
            f"{self.payment_date.strftime('%d/%m/%Y')}"
        )
    
    # =========================================================================
    # 6. MÉTODO save() (GUARDADO CON ACTUALIZACIÓN DE ESTADO)
    # =========================================================================
    
    def save(self, *args, **kwargs):
        """
        Sobreescribe save() para:
        1. Guardar el pago
        2. Verificar si la orden está completamente pagada
        3. Actualizar estado de la orden si corresponde
        """
        
        # Llamar al save() original de Django
        super().save(*args, **kwargs)
        
        # Calcular total pagado hasta el momento
        # - Sumar todos los pagos de esta orden
        total_paid = sum(payment.amount for payment in self.order.payments.all())
        
        # Verificar si el total pagado cubre o supera el total de la orden
        if total_paid >= self.order.total_amount:
            # Si está completamente pagada, actualizar estado a PAID
            self.order.status = OrderStatus.PAID
            
            # Guardar solo el campo status (evita recalcular todo)
            # update_fields optimiza la consulta SQL
            self.order.save(update_fields=['status'])
