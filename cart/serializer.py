from rest_framework.serializers import ModelSerializer
from .models import Cart, OrderItem
from products.serializer import ProductSerializer
from coupons.serializer import CouponSerializer


class OrderItemSerializer(ModelSerializer):
	product = ProductSerializer(read_only=True)

	class Meta:
		model = OrderItem
		fields = ['product', 'quantity']


class CartSerializer(ModelSerializer):
	items = OrderItemSerializer(read_only=True, many=True, source='orderitem_set')
	coupon = CouponSerializer(read_only=True)

	class Meta:
		model = Cart
		fields = '__all__'
