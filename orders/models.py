from django.db import models
from products.models import Product
from decimal import Decimal

class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    )

    id = models.UUIDField(primary_key=True, editable=False)
    stripe_session_id = models.CharField(max_length=255, unique=True)
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)

    amount_total = models.IntegerField()  # cents
    currency = models.CharField(max_length=10, default="usd")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    customer_email = models.EmailField(blank=True, null=True)

    shipping_address = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.status}"

    def save(self, *args, **kwargs):
        # Check if status is being changed to 'paid'
        if self.pk and self.status == 'paid':  # Only for existing orders being marked as paid
            try:
                old_order = Order.objects.get(pk=self.pk)
                if old_order.status != 'paid':
                    self._update_inventory()
            except Order.DoesNotExist:
                pass  # Handle case where order doesn't exist yet
        super().save(*args, **kwargs)

    def _update_inventory(self):
        """Update product inventory when order is paid"""
        for item in self.items.all():
            product = item.product
            product.inventory_count -= item.quantity
            
            # Mark as sold out if inventory reaches 0
            if product.inventory_count <= 0:
                product.inventory_count = 0
                product.is_sold_out = True
            
            product.save()

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    unit_price = models.IntegerField()  # cents (snapshot of price at time of purchase)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} x {self.quantity} for Order {self.order.id}"

    @property
    def unit_price_decimal(self):
        """Convert cents to decimal for display purposes"""
        return Decimal(self.unit_price) / Decimal(100)
