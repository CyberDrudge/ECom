from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart
from .serializer import CartSerializer
from accounts.forms import LoginForm, GuestForm
from accounts.models import GuestEmail
from addresses.forms import AddressForm, AddressCheckoutForm
from addresses.models import Address
from billing.models import BillingProfile
from orders.models import Order, OrderItem
from orders.serializer import OrderSerializer
from products.models import Product
from utility.helper import response_format

import stripe
stripe.api_key = getattr(settings, "STRIPE_API_KEY")
STRIPE_PUB_KEY = getattr(settings, "STRIPE_PUB_KEY")


# Create your views here.
def cart_detail_api_view(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    products = [{
        "id": x.id,
        "url": x.get_absolute_url(),
        "name": x.title,
        "price": x.price
    }
        for x in cart_obj.products.all()]
    cart_data = {"products": products, "subtotal": cart_obj.subtotal, "total": cart_obj.total}
    return JsonResponse(cart_data)


class CartAPIView(APIView):
    serializer_class = CartSerializer

    def post(self, request):
        cart_id = request.data.get('cart_id')
        cart_obj, new_obj = Cart.objects.new_or_get(request, cart_id)
        cart = self.serializer_class(cart_obj).data
        msg = "Cart Items"
        context = response_format(success=True, message=msg, data=cart)
        return Response(context, status.HTTP_200_OK)


# def cart_update(request):
#     # print(request.POST)
#     product_id = request.POST.get('product_id')
#     # print(product_id)
#     if product_id:
#         product_obj = Product.objects.get(id=product_id)
#         cart_obj, new_obj = Cart.objects.new_or_get(request)
#         # print(cart_obj)
#         # print(product_obj)
#         if product_obj in cart_obj.products.all():
#             cart_obj.products.remove(product_obj)
#             added = False
#         else:
#             cart_obj.products.add(product_obj)
#             added = True
#         request.session['cart_items'] = cart_obj.products.count()
#         if request.is_ajax():
#             json_data = {
#                 "added": added,
#                 "removed": not added,
#                 "cartItemCount": cart_obj.products.count()
#             }
#             return JsonResponse(json_data)
#     return redirect("cart:cartview")


class CartUpdateAPIView(APIView):
    serializer_class = CartSerializer

    def post(self, request):
        product_id = request.data.get('product_id')
        cart_id = request.data.get('cart_id')
        if product_id:
            product_obj = Product.objects.get(id=product_id)
            cart_obj, new_obj = Cart.objects.new_or_get(request, cart_id)
            if product_obj in cart_obj.products.all():
                cart_obj.products.remove(product_obj)
            else:
                cart_obj.products.add(product_obj)
                order_item_obj = OrderItem.create(product_obj)
                cart_obj.order_items.add(order_item_obj)
            # request.session['cart_items'] = cart_obj.products.count()
        cart = self.serializer_class(cart_obj).data
        msg = "Cart Updated"
        context = response_format(success=True, message=msg, data=cart)
        return Response(context, status.HTTP_200_OK)


# def checkout_home(request):
#     address_qs = None
#     has_card = False
#     if billing_profile is not None:
#         has_card = billing_profile.has_card
#
#         if request.method == "POST":
#             # is_done = order_obj.check_done()
#             # if is_done:
#             #     order_obj.mark_paid()
#             #     request.session['cart_items'] = 0
#             #     del request.session['cart_id']
#             #     return redirect('cart:checkout_success')
#             is_prepared = order_obj.check_done()
#             # print("prepared: ", is_prepared)
#             if is_prepared:
#                 did_charge, crg_msg = billing_profile.charge(order_obj)
#                 if did_charge:
#                     order_obj.mark_paid()
#                     request.session['cart_items'] = 0
#                     del request.session['cart_id']
#                     if not billing_profile.user:
#                         # ''' is this the best spot?'''
#                         billing_profile.set_cards_inactive()
#                     return redirect("cart:checkout_success")
#                 else:
#                     # print(crg_msg)
#                     return redirect("cart:checkout")
#
#     context = {
#         'object': order_obj,
#         'billing_profile': billing_profile,
#         'form': form,
#         'guest_form': guest_form,
#         'address_form': address_form,
#         'address_qs': address_qs,
#         # 'billing_address_form': billing_address_form,
#         "has_card": has_card,
#         "publish_key": STRIPE_PUB_KEY,
#     }
#     # print(billing_profile)
#     # print("Printing Context in Cart Views")
#     # print(context)
#     return render(request, 'cart/checkout.html', context)

class CheckoutHomeAPIView(APIView):
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

        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        if billing_profile is not None:
            # order_obj, order_created = Order.objects.new_or_get(billing_profile, cart_obj)
            order_obj = Order(billing_profile=billing_profile, cart=cart_obj)
            if shipping_address_id:
                order_obj.shipping_address = Address.objects.get(id=shipping_address_id)
                # del request.session['shipping_address_id']
            if billing_address_id:
                order_obj.billing_address = Address.objects.get(id=billing_address_id)
                # del request.session['billing_address_id']
            if not billing_address_id or not shipping_address_id:
                # throw error
                print("No Address Found")
            # else:
            #     order_obj.save()
            # is_prepared = order_obj.check_done()
            # print("Prep: ", is_prepared)
            # if is_prepared:
            #     did_charge, crg_msg = billing_profile.charge(order_obj)
            #     print("did_charge: ", did_charge)
            #     if did_charge:
            #         order_obj.mark_paid()
            #         message = "Checked Out"
            order_data = OrderSerializer(order_obj).data
        if not message:
            message = "Checkout Failed"
        context = response_format(success=True, message=message, data=order_data)
        return Response(context, status.HTTP_200_OK)
