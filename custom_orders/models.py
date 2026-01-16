import uuid
from django.db import models
from django.core.validators import MinValueValidator


class CustomOrderRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved - Awaiting Payment'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid - In Production'),
        ('in_production', 'In Production'),
        ('shipped', 'Shipped'),
        ('completed', 'Completed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    description = models.TextField()
    colors = models.CharField(max_length=200, blank=True, null=True)
    images = models.JSONField(default=list, help_text="List of image URLs")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    admin_notes = models.TextField(
        blank=True,
        help_text="Admin notes on pricing/timeline/rejection reason"
    )
    quoted_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text="Quoted price in USD"
    )
    stripe_payment_link = models.URLField(blank=True, null=True)
    stripe_payment_intent = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Stripe Payment Intent ID after payment"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Link to actual Order once paid
    related_order = models.OneToOneField(
        'orders.Order',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='custom_request'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Custom Order Request'
        verbose_name_plural = 'Custom Order Requests'

    def __str__(self):
        return f"Custom Order Request from {self.name} - {self.status}"
