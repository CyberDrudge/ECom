
from django.urls import path, include
from .views import (
    # cart_view, 
    # cart_update,
    checkout_home, checkout_done_view,
    CartAPIView, CartUpdateAPIView
)

app_name = 'cart'

urlpatterns = [
    # path('', cart_view, name='cartview'),
    path('', CartAPIView.as_view(), name='cartview'),
    path('checkout/success/', checkout_done_view, name='checkout_success'),
    path('checkout/', checkout_home, name='checkout'),
    # path('update/', cart_update, name='update'),
    path('update', CartUpdateAPIView.as_view(), name='update'),
]
