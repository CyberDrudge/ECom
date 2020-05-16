from rest_framework.serializers import ModelSerializer
from .models import Order
from addresses.serializer import AddressSerializer
from cart.serializer import CartSerializer

class OrderSerializer(ModelSerializer):
    billing_address = AddressSerializer()
    shipping_address = AddressSerializer()
    cart = CartSerializer()
    class Meta:
        model = Order
        fields = ['order_id', 'shipping_address', 'billing_address', 'cart', 'status', 'shipping_total', 'total']

