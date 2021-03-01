
from django.urls import path
from .views import (
    # cart_view, 
    # cart_update,
    # checkout_home,
    CartAPIView, CartUpdateAPIView, CheckoutHomeAPIView
)

app_name = 'cart'

urlpatterns = [
    path('', CartAPIView.as_view(), name='cartview'),
    path('checkout', CheckoutHomeAPIView.as_view(), name='checkout'),
    path('update', CartUpdateAPIView.as_view(), name='update'),
]
