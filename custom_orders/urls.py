from django.urls import path
from . import views

urlpatterns = [
    path('', views.submit_custom_order_request, name='submit_custom_order_request'),
]
