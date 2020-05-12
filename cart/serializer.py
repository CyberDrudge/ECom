from rest_framework.serializers import ModelSerializer
from .models import Cart
from products.serializer import ProductSerializer

class CartSerializer(ModelSerializer):
    products = ProductSerializer(read_only=True, many=True)
    class Meta:
        model = Cart
        fields = '__all__'

