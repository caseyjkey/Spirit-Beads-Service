import os
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
import mimetypes


def send_order_confirmation_email(order):
    """Send order confirmation email to customer and admin after successful checkout"""
    # Prepare order items with product details
    order_items = []
    for item in order.items.all():
        product = item.product
        order_items.append({
            'name': product.name,
            'collection': product.category.name if product.category else 'Uncategorized',
            'size': product.get_lighter_type_display(),
            'quantity': item.quantity,
            'unit_price': item.unit_price_decimal,
            'total_price': item.unit_price_decimal * item.quantity,
            'image_url': product.primary_image.url if product.primary_image else None,
        })

    # Format shipping address from JSONField
    shipping_address = order.shipping_address
    formatted_address = None
    if shipping_address:
        # Stripe address format: {line1, line2, city, state, postal_code, country}
        parts = []
        if shipping_address.get('line1'):
            parts.append(shipping_address['line1'])
        if shipping_address.get('line2'):
            parts.append(shipping_address['line2'])
        city_state_zip = []
        if shipping_address.get('city'):
            city_state_zip.append(shipping_address['city'])
        if shipping_address.get('state'):
            city_state_zip.append(shipping_address['state'])
        if shipping_address.get('postal_code'):
            city_state_zip.append(shipping_address['postal_code'])
        if city_state_zip:
            parts.append(', '.join(city_state_zip))
        if shipping_address.get('country'):
            parts.append(shipping_address['country'])
        formatted_address = '\n'.join(parts)

    # Calculate order total
    total_amount = sum(item['total_price'] for item in order_items)

    # Context for template
    context = {
        'customer_name': shipping_address.get('name', '') if shipping_address else '',
        'order_id': str(order.id),
        'order_items': order_items,
        'shipping_address': formatted_address,
        'total_amount': total_amount,
    }

    # Render email content
    subject = 'Order Confirmation - Spirit Beads'
    message = render_to_string('orders/order_confirmation_email.txt', context)

    # Create email with product images attached
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.customer_email],  # Send to customer
        cc=[settings.DEFAULT_FROM_EMAIL],  # CC to admin (lynn.braveheart@thebeadedcase.com)
    )

    # Attach product images
    for item in order_items:
        if item['image_url']:
            # Convert URL to file path
            if item['image_url'].startswith(settings.MEDIA_URL):
                relative_path = item['image_url'][len(settings.MEDIA_URL):]
                absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path)

                if os.path.exists(absolute_path):
                    filename = os.path.basename(absolute_path)
                    # Use product name in filename for clarity
                    base_name = os.path.splitext(filename)[0]
                    ext = os.path.splitext(filename)[1]
                    display_filename = f"{item['name']}-{base_name}{ext}"

                    mime_type, _ = mimetypes.guess_type(absolute_path)
                    with open(absolute_path, 'rb') as f:
                        email.attach(display_filename, f.read(), mime_type or 'image/jpeg')

    email.send(fail_silently=False)
