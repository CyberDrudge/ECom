from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Coupon
from .serializer import CouponSerializer
from utility.helper import response_format


# Create your views here.
class CouponDetailView(APIView):
	queryset = Coupon.objects
	serializer_class = CouponSerializer

	def get(self, request):
		code = request.GET.get('code', None)
		print(request.GET)
		print("Code: ", code)
		if code is None:
			return Response({"message": "Invalid data received"}, status=status.HTTP_200_OK)
		coupon = Coupon.objects.get_by_code(code)
		if coupon is None:
			return Response({"message": "Coupon Expired"}, status=status.HTTP_200_OK)

		context = self.serializer_class(coupon).data
		msg = "Code Applied"
		context = response_format(True, msg, context)
		return Response(context, status.HTTP_200_OK)
