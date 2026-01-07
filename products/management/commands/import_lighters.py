import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.files import File
from django.db import transaction
from decimal import Decimal
from products.models import Product, Category
import uuid

class Command(BaseCommand):
    help = 'Import lighter images from directory using filename format: Name_Category_Price-1.png (primary) and Name_Category_Price-2.png (secondary)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'directory',
            type=str,
            help='Path to directory containing lighter images'
        )
        parser.add_argument(
            '--lighter-type',
            type=int,
            choices=[1, 2],
            default=1,
            help='Lighter type (1=Classic BIC, 2=Mini BIC)'
        )
        parser.add_argument(
            '--pattern',
            type=str,
            default='custom',
            help='Pattern type (defaults to custom)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making changes to database'
        )
    
    def handle(self, *args, **options):
        directory = Path(options['directory'])
        
        if not directory.exists():
            self.stdout.write(self.style.ERROR(f'Directory not found: {directory}'))
            return
        
        self.dry_run = options['dry_run']
        lighter_type = options['lighter_type']
        pattern = options['pattern']
        
        if self.dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made to database'))
        
        # Group images by base name (Name_Category_Price)
        image_groups = {}
        
        for image_file in directory.glob('*.png'):
            try:
                parsed = self.parse_filename(image_file.name)
                base_name = parsed['base_name']
                
                if base_name not in image_groups:
                    image_groups[base_name] = {}
                
                if parsed['is_primary']:
                    image_groups[base_name]['primary'] = image_file
                else:
                    image_groups[base_name]['secondary'] = image_file
                    
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Error parsing {image_file.name}: {e}')
                )
                continue
        
        if not image_groups:
            self.stdout.write(self.style.WARNING('No valid image files found'))
            return
        
        self.stdout.write(f'Found {len(image_groups)} image groups to process')
        
        # Create Product objects
        created_count = 0
        skipped_count = 0
        error_count = 0
        
        for base_name, images in image_groups.items():
            if 'primary' not in images:
                self.stdout.write(
                    self.style.WARNING(f'Missing primary image for {base_name}')
                )
                continue
            
            try:
                with transaction.atomic():
                    result = self.process_image_group(base_name, images, lighter_type, pattern)
                    if result == 'created':
                        created_count += 1
                    elif result == 'skipped':
                        skipped_count += 1
                        
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'Error processing {base_name}: {e}')
                )
                continue
        
        summary = f'\nImport complete: {created_count} created, {skipped_count} skipped, {error_count} errors'
        if self.dry_run:
            summary = f'DRY RUN - {summary}'
        
        self.stdout.write(self.style.SUCCESS(summary))
    
    def process_image_group(self, base_name, images, lighter_type, pattern):
        """Process a group of images (primary and optional secondary)"""
        # Parse to get metadata from primary image
        parsed = self.parse_filename(images['primary'].name)
        
        # Generate a unique product ID
        product_id = str(uuid.uuid4())
        
        # Convert price from dollars to cents (your model stores price in cents)
        price_cents = int(parsed['price'] * 100)
        
        # Check if product already exists by checking name, pattern, and price
        existing_products = Product.objects.filter(
            name=parsed['name'],
            pattern=pattern,
            price=price_cents
        )
        
        if existing_products.exists():
            product_name = f"{parsed['name']} - {parsed['category']}"
            self.stdout.write(
                self.style.WARNING(f'Skipping existing product: {product_name}')
            )
            return 'skipped'
        
        if self.dry_run:
            self.stdout.write(f'Would create: {parsed["name"]} - {parsed["category"]} (${parsed["price"]:.2f})')
            return 'created'
        
        # Create or get category
        category, created = Category.objects.get_or_create(
            name=parsed['category'],
            defaults={'slug': parsed['category'].lower().replace('-', '-')}
        )
        
        # Create the product
        product = Product.objects.create(
            id=product_id,
            name=parsed['name'],
            slug=f"{parsed['name'].lower().replace(' ', '-')}-{product_id[:8]}",
            lighter_type=lighter_type,
            pattern=pattern,
            custom_pattern=parsed['category'] if pattern == 'custom' else '',
            price=price_cents,
            description=f"Beautiful {parsed['category']} pattern lighter - {parsed['name']}"
        )
        
        # Save primary image
        with open(images['primary'], 'rb') as f:
            product.primary_image.save(
                images['primary'].name,
                File(f),
                save=True
            )
        
        # Save secondary image if available
        if 'secondary' in images:
            with open(images['secondary'], 'rb') as f:
                product.secondary_image.save(
                    images['secondary'].name,
                    File(f),
                    save=True
                )
        
        product_name = f"{parsed['name']} - {parsed['category']}"
        self.stdout.write(
            self.style.SUCCESS(f'Created: {product_name} (${parsed["price"]:.2f})')
        )
        
        return 'created'
    
    def parse_filename(self, filename):
        """Parse filename and return metadata."""
        name_without_ext = Path(filename).stem
        parts = name_without_ext.split('_')
        
        if len(parts) < 3:
            raise ValueError(f"Invalid filename format: {filename}")
        
        # Last part contains price and side: "55-1" or "55-2"
        price_side = parts[-1]
        price_str, side_str = price_side.split('-')
        
        # Extract fields
        name = parts[0]  # "Feather-Sun"
        category = '_'.join(parts[1:-1])  # Join middle parts for category (handles categories with underscores)
        price = float(price_str)  # Convert to float for price in dollars
        side = int(side_str)  # 1 or 2
        
        return {
            'name': name,
            'category': category,
            'price': price,
            'side': side,
            'is_primary': (side == 1),
            'is_secondary': (side == 2),
            'base_name': f"{name}_{category}_{price_str}"
        }
