import uuid
import os
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from .models import CustomOrderRequest
from .utils import send_new_request_notification
import json


def detect_image_type(file_content):
    """Detect image type from file header bytes."""
    # Image file signatures (magic numbers)
    signatures = {
        b'\xFF\xD8\xFF': 'jpeg',
        b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A': 'png',
        b'RIFF': 'webp',  # WebP starts with RIFF and has WEBP in bytes 8-11
        b'GIF87a': 'gif',
        b'GIF89a': 'gif',
    }

    for signature, img_type in signatures.items():
        if file_content.startswith(signature):
            # Additional check for WebP
            if img_type == 'webp' and len(file_content) >= 12:
                if file_content[8:12] != b'WEBP':
                    continue
            return img_type

    return None


@csrf_exempt
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def submit_custom_order_request(request):
    """
    Submit a custom order request.

    Supports two formats:
    1. multipart/form-data: For file uploads (recommended)
       - name, email, description, colors (text fields)
       - images (file field, multiple files allowed)

    2. application/json: For backward compatibility
       - name, email, description, colors, images (base64 or URLs)
    """
    # Determine content type and parse accordingly
    content_type = request.content_type or ''

    if 'multipart/form-data' in content_type:
        # Handle file uploads via FormData
        return _handle_formdata_upload(request)
    else:
        # Handle JSON payload (backward compatibility)
        return _handle_json_upload(request)


def _handle_formdata_upload(request):
    """Handle multipart/form-data file uploads"""
    from django.core.files.uploadedfile import InMemoryUploadedFile

    # Validate required fields
    required_fields = ['name', 'email', 'description']
    for field in required_fields:
        if field not in request.POST:
            return Response(
                {"error": f"Missing required field: {field}"},
                status=400
            )

    # Validate email format
    email = request.POST['email'].strip()
    if '@' not in email or '.' not in email:
        return Response({"error": "Invalid email address"}, status=400)

    # Validate description length
    description = request.POST['description'].strip()
    if len(description) < 10:
        return Response(
            {"error": "Description must be at least 10 characters"},
            status=400
        )

    # Extract optional fields
    colors = request.POST.get('colors', '').strip() if request.POST.get('colors') else None

    # Handle file uploads
    images = []
    uploaded_files = request.FILES.getlist('images')

    # File upload restrictions
    MAX_FILE_SIZE = 7 * 1024 * 1024  # 7MB per file
    MAX_FILES = 10
    ALLOWED_IMAGE_TYPES = {
        'jpeg': '.jpg',
        'png': '.png',
        'webp': '.webp',
        'gif': '.gif',
    }

    if len(uploaded_files) > MAX_FILES:
        return Response(
            {"error": f"Maximum {MAX_FILES} images allowed"},
            status=400
        )

    for i, uploaded_file in enumerate(uploaded_files):
        # Check file size
        if uploaded_file.size > MAX_FILE_SIZE:
            return Response(
                {"error": f"Image {i+1} exceeds {MAX_FILE_SIZE // (1024*1024)}MB limit"},
                status=400
            )

        # Validate image type by reading file content
        file_content = uploaded_file.read()
        uploaded_file.seek(0)  # Reset pointer

        image_type = detect_image_type(file_content)
        if image_type not in ALLOWED_IMAGE_TYPES:
            return Response(
                {"error": f"Image {i+1} is not a valid image type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES.keys())}"},
                status=400
            )

        # Save file to media/custom_orders/
        filename = f"{uuid.uuid4()}{ALLOWED_IMAGE_TYPES[image_type]}"
        save_path = os.path.join('custom_orders', filename)

        try:
            saved_path = default_storage.save(save_path, uploaded_file)
            # Store relative URL that can be accessed via MEDIA_URL
            images.append(f"{settings.MEDIA_URL}{saved_path}")
        except Exception as e:
            print(f"Error saving image {i+1}: {e}")
            return Response(
                {"error": f"Failed to save image {i+1}"},
                status=500
            )

    # Create custom order request
    try:
        custom_request = CustomOrderRequest.objects.create(
            id=uuid.uuid4(),
            name=request.POST['name'].strip(),
            email=email,
            description=description,
            colors=colors,
            images=images,
            status='pending'
        )
    except Exception as e:
        print(f"Error creating custom order request: {e}")
        return Response(
            {"error": "Failed to create request", "details": str(e)},
            status=500
        )

    # Send email notification to admin
    try:
        send_new_request_notification(custom_request)
    except Exception as e:
        print(f"Error sending email notification: {e}")
        # Don't fail the request if email fails

    return Response({
        "success": True,
        "message": "Custom order request submitted successfully!",
        "request_id": str(custom_request.id)
    }, status=201)


def _handle_json_upload(request):
    """Handle JSON payload with base64 or URL images (backward compatibility)"""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON"}, status=400)

    # Validate required fields
    required_fields = ['name', 'email', 'description']
    for field in required_fields:
        if not data.get(field):
            return Response(
                {"error": f"Missing required field: {field}"},
                status=400
            )

    # Validate email format
    email = data['email'].strip()
    if '@' not in email or '.' not in email:
        return Response({"error": "Invalid email address"}, status=400)

    # Validate description length
    description = data['description'].strip()
    if len(description) < 10:
        return Response(
            {"error": "Description must be at least 10 characters"},
            status=400
        )

    # Extract optional fields
    colors = data.get('colors', '').strip() if data.get('colors') else None

    # Handle images - expect base64 encoded strings or URLs
    images = []
    if 'images' in data and data['images']:
        images_data = data['images']
        if isinstance(images_data, list):
            # Handle list of objects with preview/preview properties
            for img in images_data:
                if isinstance(img, dict) and 'preview' in img:
                    images.append(img['preview'])
                elif isinstance(img, str):
                    images.append(img)
            # Also check FileList (browser native)
            if hasattr(images_data, 'length'):
                for i in range(images_data.length):
                    item = images_data[i]
                    if hasattr(item, 'preview'):
                        images.append(item.preview)

    # Create custom order request
    try:
        custom_request = CustomOrderRequest.objects.create(
            id=uuid.uuid4(),
            name=data['name'].strip(),
            email=email,
            description=description,
            colors=colors,
            images=images,
            status='pending'
        )
    except Exception as e:
        print(f"Error creating custom order request: {e}")
        return Response(
            {"error": "Failed to create request", "details": str(e)},
            status=500
        )

    # Send email notification to admin
    try:
        send_new_request_notification(custom_request)
    except Exception as e:
        print(f"Error sending email notification: {e}")
        # Don't fail the request if email fails

    return Response({
        "success": True,
        "message": "Custom order request submitted successfully!",
        "request_id": str(custom_request.id)
    }, status=201)
