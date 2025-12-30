from django.db import migrations
from decimal import Decimal

def create_initial_products(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    
    products_data = [
        {
            'name': 'Desert Diamond',
            'slug': 'desert-diamond',
            'pattern': 'chevron',
            'pattern_description': 'Chevron Pattern',
            'price': Decimal('45.00'),
            'inventory_count': 1,
        },
        {
            'name': 'Turquoise Trail',
            'slug': 'turquoise-trail',
            'pattern': 'geometric',
            'pattern_description': 'Geometric Pattern',
            'price': Decimal('48.00'),
            'inventory_count': 1,
        },
        {
            'name': 'Sunburst Spirit',
            'slug': 'sunburst-spirit',
            'pattern': 'sunburst',
            'pattern_description': 'Sunburst Pattern',
            'price': Decimal('52.00'),
            'inventory_count': 1,
        },
        {
            'name': 'Sacred Stone',
            'slug': 'sacred-stone',
            'pattern': 'diamond',
            'pattern_description': 'Diamond Pattern',
            'price': Decimal('46.00'),
            'inventory_count': 1,
        },
        {
            'name': 'Forest Fire',
            'slug': 'forest-fire',
            'pattern': 'mountain',
            'pattern_description': 'Mountain Pattern',
            'price': Decimal('50.00'),
            'inventory_count': 1,
        },
        {
            'name': 'Rainbow Ridge',
            'slug': 'rainbow-ridge',
            'pattern': 'arrow',
            'pattern_description': 'Arrow Pattern',
            'price': Decimal('55.00'),
            'is_sold_out': True,
            'inventory_count': 0,
        },
    ]
    
    for product_data in products_data:
        Product.objects.create(**product_data)

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_products),
    ]
