from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def send_new_request_notification(custom_request):
    """Send email notification to admin about new custom order request"""
    subject = f'New Custom Order Request from {custom_request.name}'

    message = render_to_string('custom_orders/new_request_email.txt', {
        'name': custom_request.name,
        'email': custom_request.email,
        'description': custom_request.description,
        'colors': custom_request.colors,
        'images': custom_request.images,
    })

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.DEFAULT_FROM_EMAIL],  # Admin receives notification
        fail_silently=False,
    )


def send_approval_email(custom_request):
    """Send email to customer when custom order is approved with payment link"""
    subject = f'Your Custom Order Request Has Been Approved!'

    message = render_to_string('custom_orders/approved_email.txt', {
        'name': custom_request.name,
        'description': custom_request.description,
        'colors': custom_request.colors,
        'quoted_price': custom_request.quoted_price,
        'stripe_payment_link': custom_request.stripe_payment_link,
    })

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[custom_request.email],
        fail_silently=False,
    )


def send_payment_confirmation_email(custom_request, order):
    """Send email to customer confirming payment was received"""
    subject = 'Payment Received - Your Custom Order is in Production!'

    message = render_to_string('custom_orders/payment_received_email.txt', {
        'name': custom_request.name,
        'order_id': order.id,
        'amount_total': order.amount_total / 100,  # Convert cents to dollars
        'quoted_price': custom_request.quoted_price,
        'description': custom_request.description,
        'colors': custom_request.colors,
    })

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[custom_request.email],
        fail_silently=False,
    )


def send_rejection_email(custom_request):
    """Send email to customer when custom order is rejected"""
    subject = 'Update on Your Custom Order Request'

    message = render_to_string('custom_orders/rejected_email.txt', {
        'name': custom_request.name,
        'description': custom_request.description,
        'colors': custom_request.colors,
        'rejection_reason': custom_request.admin_notes,
    })

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[custom_request.email],
        fail_silently=False,
    )


def send_shipped_email(custom_request, order, tracking_number=None, carrier='USPS'):
    """Send email to customer when custom order ships"""
    subject = 'Your Custom Order Has Shipped!'

    message = render_to_string('custom_orders/shipped_email.txt', {
        'name': custom_request.name,
        'order_id': order.id,
        'tracking_number': tracking_number,
        'shipping_carrier': carrier,
        'shipped_date': order.updated_at.strftime('%B %d, %Y'),
        'description': custom_request.description,
        'colors': custom_request.colors,
    })

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[custom_request.email],
        fail_silently=False,
    )
