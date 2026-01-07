# Spirit Bead Backend

Django backend for the Spirit Bead e-commerce platform.

## Setup

1. Activate virtual environment:
```bash
source venv/bin/activate
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Start the development server:
```bash
python manage.py runserver
```

## Product Image Import

This project includes a management command to import lighter product images from filenames.

### Image Naming Convention

Images must follow this pattern:
- **Primary/Front Image**: `Name_Category_Price-1.png` 
- **Secondary/Back Image**: `Name_Category_Price-2.png`

**Examples:**
- `Feather-Sun_Infinite-Path_55-1.png` (primary image)
- `Feather-Sun_Infinite-Path_55-2.png` (secondary image)
- `Mountain-View_Earths-Hue_45-1.png` (primary image)
- `Mountain-View_Earths-Hue_45-2.png` (secondary image)

### Import Process

1. **Add images to media folder:**
   Place your PNG images in the `media/products/` directory:
   ```bash
   # Copy your images to the media folder
   cp /path/to/your/images/*.png media/products/
   ```

2. **Run the import command:**
   ```bash
   source venv/bin/activate
   
   # Test first (recommended)
   python manage.py import_lighters media/products/ --dry-run
   
   # Run actual import
   python manage.py import_lighters media/products/
   ```

### Command Options

- `--lighter-type {1,2}` - Lighter type (1=Classic BIC, 2=Mini BIC, default: 1)
- `--pattern PATTERN` - Pattern type (default: 'custom')
- `--dry-run` - Test without making database changes

**Examples:**
```bash
# Import Mini BIC lighters
python manage.py import_lighters media/products/ --lighter-type 2

# Import with specific pattern
python manage.py import_lighters media/products/ --pattern chevron

# Test run to see what would be imported
python manage.py import_lighters media/products/ --dry-run
```

### What Gets Created

1. **Products** - One product per image pair (Name_Category_Price)
2. **Categories** - Auto-created from filename categories
3. **Image assignments**:
   - `*-1.png` → Primary image
   - `*-2.png` → Secondary image (if present)

### Duplicate Prevention

The command automatically skips products that already exist to prevent duplicates. It checks for existing products with the same:
- Name
- Pattern  
- Price

### Field Mapping

| Filename Part | Product Field | Example |
|--------------|--------------|---------|
| `Name` (first part) | `name` | "Feather-Sun" |
| `Category` (second part) | `custom_pattern` | "Infinite-Path" |
| `Price` (third part, before `-`) | `price` | 55 (stored as 5500 cents) |
| `-1` suffix | `primary_image` | Front image |
| `-2` suffix | `secondary_image` | Back image |

### Troubleshooting

- **"Invalid filename format"** - Check that filenames follow the `Name_Category_Price-#.png` pattern
- **"Missing primary image"** - Every product needs a `*-1.png` file
- **"Directory not found"** - Ensure the path to your images is correct
- **"No valid image files found"** - Make sure you have PNG files in the directory

## Database Seeding

This project includes a management command to seed the database with test products and categories.

### Quick Start

To seed the database with sample products:

```bash
source venv/bin/activate

# Seed with default 5 classic and 2 mini lighters
python manage.py seed

# Clear existing data and seed fresh
python manage.py seed --clear
```

### What Gets Created

1. **Categories** - 5 categories including one empty category:
   - Tribal Patterns (with products)
   - Nature Inspired (with products)
   - Geometric Shapes (with products)
   - Spiritual Symbols (with products)
   - Abstract Art (empty)

2. **Products** - Test products with:
   - 5 Classic BIC lighters (size 1)
   - 2 Mini BIC lighters (size 2)
   - Random prices between $20.00 and $5,550.00
   - Primary and secondary images for each product
   - Products distributed across categories

### Command Options

- `--clear` - Remove all existing products and categories before seeding
- `--count-classic N` - Number of classic lighters to create (default: 5)
- `--count-mini N` - Number of mini lighters to create (default: 2)

**Examples:**
```bash
# Create 10 classic and 5 mini lighters
python manage.py seed --count-classic 10 --count-mini 5

# Clear database and create custom amounts
python manage.py seed --clear --count-classic 3 --count-mini 1
```

### Generated Images

The seed command automatically generates test images that are:
- Stored in `media/products/` (excluded from git)
- 200x200 PNG files with product names
- Random colors for visual variety
- Properly formatted for the import system

### After Seeding

After running the seed command:
- Visit `http://localhost:8000/admin/` to view products
- Products will be available through the API endpoints
- Images are served from `/media/products/`

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Superuser
```bash
python manage.py createsuperuser
```

### Admin Access
Visit `http://localhost:8000/admin/` after starting the server to access the Django admin interface.
