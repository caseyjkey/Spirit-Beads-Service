import os
import random
import subprocess
import tempfile
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command
from products.models import Category, Product
import uuid

class Command(BaseCommand):
    help = 'Seed the database with test products and categories'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing products and categories before seeding'
        )
        parser.add_argument(
            '--count-classic',
            type=int,
            default=5,
            help='Number of classic lighters to create (default: 5)'
        )
        parser.add_argument(
            '--count-mini',
            type=int,
            default=2,
            help='Number of mini lighters to create (default: 2)'
        )
    
    def handle(self, *args, **options):
        clear_existing = options['clear']
        count_classic = options['count_classic']
        count_mini = options['count_mini']
        
        if clear_existing:
            self.stdout.write(self.style.WARNING('Clearing existing products and categories...'))
            Product.objects.all().delete()
            Category.objects.all().delete()
        
        # Create categories
        self.create_categories()
        
        # Generate test images
        with tempfile.TemporaryDirectory() as temp_dir:
            self.stdout.write('Generating test images...')
            self.generate_test_images(temp_dir, count_classic, count_mini)
            
            # Import classic lighters
            if count_classic > 0:
                self.stdout.write(f'Importing {count_classic} classic lighters...')
                call_command('import_lighters', temp_dir, '--lighter-type', '1', '--pattern', 'custom')
            
            # Import mini lighters  
            if count_mini > 0:
                self.stdout.write(f'Importing {count_mini} mini lighters...')
                call_command('import_lighters', temp_dir, '--lighter-type', '2', '--pattern', 'custom')
        
        self.stdout.write(self.style.SUCCESS('Database seeding complete!'))
        self.display_summary()
    
    def create_categories(self):
        """Create categories including one empty category"""
        categories_data = [
            ('Tribal Patterns', 'tribal-patterns', 'Traditional tribal and indigenous designs'),
            ('Nature Inspired', 'nature-inspired', 'Designs inspired by natural elements'),
            ('Geometric Shapes', 'geometric-shapes', 'Modern geometric patterns and shapes'),
            ('Spiritual Symbols', 'spiritual-symbols', 'Sacred and spiritual symbolism'),
            ('Abstract Art', 'abstract-art', 'Contemporary abstract designs'),  # This will be empty initially
        ]
        
        for name, slug, description in categories_data:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={
                    'slug': slug,
                    'description': description
                }
            )
            if created:
                self.stdout.write(f'Created category: {name}')
            else:
                self.stdout.write(f'Category already exists: {name}')
    
    def generate_test_images(self, temp_dir, count_classic, count_mini):
        """Generate test images using create_test_images.py"""
        # Define product data
        classic_products = [
            ('Eagle-Feather', 'Tribal-Patterns'),
            ('Mountain-Spirit', 'Nature-Inspired'),
            ('Sacred-Geometry', 'Geometric-Shapes'),
            ('Wolf-Totem', 'Spiritual-Symbols'),
            ('Desert-Sun', 'Tribal-Patterns'),
        ]
        
        mini_products = [
            ('Mini-Eagle', 'Tribal-Patterns'),
            ('Mini-Geometry', 'Geometric-Shapes'),
        ]
        
        # Generate images for classic lighters
        for i, (name, category) in enumerate(classic_products[:count_classic]):
            price = random.randint(2000, 555000)  # Random price in cents
            price_dollars = price / 100
            
            # Primary image
            self.create_single_image(temp_dir, f"{name}_{category}_{price_dollars}-1.png", f"{name}\nPrimary")
            
            # Secondary image
            self.create_single_image(temp_dir, f"{name}_{category}_{price_dollars}-2.png", f"{name}\nSecondary")
        
        # Generate images for mini lighters
        for i, (name, category) in enumerate(mini_products[:count_mini]):
            price = random.randint(2000, 555000)  # Random price in cents
            price_dollars = price / 100
            
            # Primary image
            self.create_single_image(temp_dir, f"{name}_{category}_{price_dollars}-1.png", f"{name}\nPrimary")
            
            # Secondary image
            self.create_single_image(temp_dir, f"{name}_{category}_{price_dollars}-2.png", f"{name}\nSecondary")
    
    def create_single_image(self, temp_dir, filename, text):
        """Create a single test image using the existing create_test_images.py logic"""
        from PIL import Image, ImageDraw, ImageFont
        
        # Generate random color for variety
        color = (
            random.randint(50, 200),
            random.randint(50, 200),
            random.randint(50, 200)
        )
        
        # Create a simple 200x200 image
        img = Image.new('RGB', (200, 200), color)
        draw = ImageDraw.Draw(img)
        
        # Add text to identify the image
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        # Draw text in the center
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (200 - text_width) // 2
        y = (200 - text_height) // 2
        
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        
        # Save as PNG
        filepath = Path(temp_dir) / filename
        img.save(filepath, 'PNG')
    
    def display_summary(self):
        """Display summary of created data"""
        category_count = Category.objects.count()
        product_count = Product.objects.count()
        classic_count = Product.objects.filter(lighter_type=1).count()
        mini_count = Product.objects.filter(lighter_type=2).count()
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('SEEDING SUMMARY'))
        self.stdout.write('='*50)
        self.stdout.write(f'Categories: {category_count}')
        self.stdout.write(f'Total Products: {product_count}')
        self.stdout.write(f'  - Classic Lighters: {classic_count}')
        self.stdout.write(f'  - Mini Lighters: {mini_count}')
        
        # Show categories with product counts
        self.stdout.write('\nProducts by Category:')
        for category in Category.objects.all():
            count = Product.objects.filter(category=category).count()
            status = "EMPTY" if count == 0 else f"{count} products"
            self.stdout.write(f'  - {category.name}: {status}')
        
        self.stdout.write('='*50)
