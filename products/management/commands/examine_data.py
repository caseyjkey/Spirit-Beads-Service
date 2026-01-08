from django.core.management.base import BaseCommand
from products.models import Category, Product

class Command(BaseCommand):
    help = 'Examine current categories and products with custom patterns'

    def handle(self, *args, **options):
        self.stdout.write('=== CATEGORIES ===')
        categories = Category.objects.all()
        for category in categories:
            self.stdout.write(f'  {category.name}')
        
        self.stdout.write('\n=== PRODUCTS WITH CATEGORIES ===')
        products_with_categories = Product.objects.filter(category__isnull=False)
        for product in products_with_categories:
            self.stdout.write(f'  {product.name} - {product.category.name if product.category else "None"}')
        
        self.stdout.write(f'\nTotal categories: {categories.count()}')
        self.stdout.write(f'Total products with categories: {products_with_categories.count()}')
