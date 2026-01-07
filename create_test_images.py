#!/usr/bin/env python3
"""
Create test images for import_lighters command
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image(filename, text, color=(100, 150, 200)):
    """Create a simple test image with text"""
    # Create a simple 200x200 image
    img = Image.new('RGB', (200, 200), color)
    draw = ImageDraw.Draw(img)
    
    # Add text to identify the image
    try:
        # Try to use a default font
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
    img.save(filename, 'PNG')
    print(f"Created: {filename}")

def main():
    # Create test directory
    test_dir = Path("/tmp/test_lighters")
    test_dir.mkdir(exist_ok=True)
    
    # Test cases based on the specification
    test_cases = [
        # Basic case
        ("Feather-Sun_Infinite-Path_55-1.png", "Feather-Sun\nPrimary", (100, 150, 200)),
        ("Feather-Sun_Infinite-Path_55-2.png", "Feather-Sun\nSecondary", (200, 150, 100)),
        
        # Different categories
        ("Mountain-View_Earths-Hue_45-1.png", "Mountain-View\nPrimary", (150, 200, 100)),
        ("Mountain-View_Earths-Hue_45-2.png", "Mountain-View\nSecondary", (100, 200, 150)),
        
        ("Ocean-Wave_Traditional-Rhythms_60-1.png", "Ocean-Wave\nPrimary", (200, 100, 150)),
        ("Ocean-Wave_Traditional-Rhythms_60-2.png", "Ocean-Wave\nSecondary", (150, 100, 200)),
        
        # Single image (no secondary)
        ("Desert-Rose_Ancestral-Motifs_50-1.png", "Desert-Rose\nPrimary", (180, 180, 100)),
        
        # Complex name with hyphens
        ("Double-Eagle_Spirit-Path_75-1.png", "Double-Eagle\nPrimary", (120, 180, 180)),
        ("Double-Eagle_Spirit-Path_75-2.png", "Double-Eagle\nSecondary", (180, 120, 180)),
    ]
    
    for filename, text, color in test_cases:
        filepath = test_dir / filename
        create_test_image(filepath, text, color)
    
    print(f"\nCreated {len(test_cases)} test images in {test_dir}")
    print("You can now test the import with:")
    print(f"python manage.py import_lighters {test_dir} --dry-run")

if __name__ == "__main__":
    main()
