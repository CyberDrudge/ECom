from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic import ListView, DetailView
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order
from cart.models import Cart
from addresses.models import Address
from billing.models import BillingProfile
from .serializer import OrderSerializer
from utility.helper import response_format

import stripe
stripe.api_key = getattr(settings, "STRIPE_API_KEY")
STRIPE_PUB_KEY = getattr(settings, "STRIPE_PUB_KEY")


# Create your views here.
class OrderListView(LoginRequiredMixin, ListView):

    def get_queryset(self):
        return Order.objects.by_request(self.request).not_created()


class OrderDetailView(LoginRequiredMixin, DetailView):

    def get_object(self):
        qs = Order.objects.by_request(
                    self.request
                ).filter(
                    order_id=self.kwargs.get('order_id')
                )
        if qs.count() == 1:
            return qs.first()
        raise Http404


class PlaceOrderAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        cart_id = request.data.get('cart_id')
        cart_obj, new_cart = Cart.objects.new_or_get(request, cart_id)
        message = ""
        # XNOTE: if new_cart or cart_obj.products.count() == 0:
        # return error
        #  XNOTE: return if user not authenticated
        if not cart_obj.user:
            cart_obj.user = user
            cart_obj.save()
        order_obj = None
        billing_address_id = request.data.get('billing_address_id', None)
        shipping_address_id = request.data.get('shipping_address_id', None)
        token = request.data.get('token', None)
        print("Token", token)
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        if billing_profile is not None:
            order_obj, order_created = Order.objects.new_or_get(billing_profile, cart_obj)
            if shipping_address_id:
                order_obj.shipping_address = Address.objects.get(id=shipping_address_id)
                # del request.session['shipping_address_id']
            if billing_address_id:
                order_obj.billing_address = Address.objects.get(id=billing_address_id)
                # del request.session['billing_address_id']
            if not billing_address_id or not shipping_address_id:
                # throw error
                print("No Address Found")
            else:
                order_obj.save()
            is_prepared = order_obj.check_done()
            print("Prep: ", is_prepared)
            if is_prepared:
                did_charge, crg_msg = billing_profile.charge(order_obj, token=token)
                print("did_charge: ", did_charge)
                if did_charge:
                    order_obj.mark_paid()
                    message = "Checked Out"
            order_data = OrderSerializer(order_obj).data
        if not message:
            message = "Checkout Failed"
        context = response_format(success=True, message=message, data=order_data)
        return Response(context, status.HTTP_200_OK)
