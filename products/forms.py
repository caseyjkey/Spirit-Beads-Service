from django import forms
from decimal import Decimal, InvalidOperation
from .models import Product

class ProductAdminForm(forms.ModelForm):
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
        help_text="Enter price in decimal format (e.g., 45.99). Currency is USD.",
        error_messages={
            'invalid': 'Enter a valid price using numbers and a decimal point only (e.g., 25.99).',
            'max_digits': 'Price cannot exceed $9,999,999.99.',
            'max_decimal_places': 'Price can have at most 2 decimal places (e.g., 25.99, not 25.999).',
            'min_value': 'Price must be at least $0.01.',
        }
    )
    
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Convert cents back to decimal for display
        if self.instance and self.instance.pk and hasattr(self.instance, 'price') and self.instance.price:
            decimal_price = Decimal(self.instance.price) / Decimal('100')
            self.initial['price'] = decimal_price
        
        # Make currency field read-only
        if 'currency' in self.fields:
            self.fields['currency'].widget.attrs['readonly'] = True
            self.fields['currency'].widget.attrs['disabled'] = True

    def clean_price(self):
        """
        Convert decimal price to cents for storage with enhanced validation
        """
        price_data = self.cleaned_data.get('price')
        
        if price_data is None:
            return price_data
            
        # Additional custom validation
        if price_data > Decimal('999999.99'):
            raise forms.ValidationError("Price cannot exceed $999,999.99.")
        
        # Convert to cents for storage
        return int(price_data * Decimal('100'))

    def get_initial_for_field(self, field, field_name):
        """
        Override to provide proper initial value for price field
        """
        if field_name == 'price' and self.instance and self.instance.pk and hasattr(self.instance, 'price') and self.instance.price:
            decimal_price = Decimal(self.instance.price) / Decimal('100')
            return decimal_price
        return super().get_initial_for_field(field, field_name)
