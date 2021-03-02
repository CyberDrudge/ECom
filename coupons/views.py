from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Coupon
from cart.models import Cart
from cart.serializer import CartSerializer
from utility.helper import response_format


# Create your views here.
class CouponDetailView(APIView):
	queryset = Coupon.objects
	serializer_class = CartSerializer

	def get(self, request):
		code = request.GET.get('code', None)
		cart_id = request.GET.get('cart_id', None)
		if code is None:
			return Response({"message": "Invalid Data Received"}, status=status.HTTP_200_OK)
		coupon = self.queryset.get_by_code(code)
		print(coupon)
		if coupon is None:
			return Response({"message": "Invalid Coupon"}, status=status.HTTP_200_OK)
		if cart_id:
			cart_obj, new_obj = Cart.objects.new_or_get(request, cart_id)
			cart_obj.coupon = coupon
			cart_obj.save()
			print(cart_obj)
			context = self.serializer_class(cart_obj).data
		else:
			context = {}
		msg = "Code Applied"
		context = response_format(True, msg, context)
		return Response(context, status.HTTP_200_OK)
