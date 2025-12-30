from django.contrib import admin
from .models import Product, Category, ProductImage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'order']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_pattern_display', 'price', 'inventory_count', 'is_sold_out', 'is_active']
    list_filter = ['pattern', 'is_sold_out', 'is_active', 'created_at']
    search_fields = ['name', 'custom_pattern']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ProductImageInline]
    
    class Media:
        js = ('products/js/admin_custom_pattern.js', 'products/js/admin_custom_pattern_vanilla.js')
        css = {
            'all': ('products/css/admin_custom_pattern.css',)
        }
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'pattern', 'custom_pattern', 'description')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'inventory_count', 'is_sold_out', 'is_active')
        }),
        ('Shipping', {
            'fields': ('weight_ounces',)
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'alt_text', 'is_primary', 'order']
    list_filter = ['is_primary']
    ordering = ['product', 'order']
