from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Cart
from .serializer import CartSerializer
from accounts.forms import LoginForm, GuestForm
from accounts.models import GuestEmail
from addresses.forms import AddressForm, AddressCheckoutForm
from addresses.models import Address
from billing.models import BillingProfile
from orders.models import Order
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


# def cart_view(request):
#     cart_obj, new_obj = Cart.objects.new_or_get(request)
#     context = {
#         'cart': cart_obj
#     }
#     return render(request, 'cart/home.html', context)


class CartAPIView(APIView):
    serializer_class = CartSerializer
    def post(self, request):
        cart_id = request.data.get('cart_id')
        print(cart_id)
        cart_obj, new_obj = Cart.objects.new_or_get(request, cart_id)
        # cart_obj = Cart.objects.get(id=106)
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
                added = False
            else:
                cart_obj.products.add(product_obj)
                added = True
            request.session['cart_items'] = cart_obj.products.count()
        cart = self.serializer_class(cart_obj).data
        msg = "Cart Updated"
        context = response_format(success=True, message=msg, data=cart)
        return Response(context, status.HTTP_200_OK)



def checkout_home(request):
    # print("In checkout home")
    cart_obj, new_cart = Cart.objects.new_or_get(request)
    # print(cart_obj, new_cart)
    order_obj = None
    if new_cart or cart_obj.products.count() == 0:
        return redirect('cart:cartview')
    # else:
    #     print(cart_obj)
    #     order_obj, new_order = Order.objects.get_or_create(cart=cart_obj)
    #     print(order_obj, new_order)

    form = LoginForm(request=request)
    guest_form = GuestForm(request=request)
    address_form = AddressCheckoutForm()
    # billing_address_form = AddressForm()
    billing_address_id = request.session.get('billing_address_id', None)
    shipping_address_id = request.session.get('shipping_address_id', None)

    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    # print(billing_profile, billing_profile_created)
    # guest_email_id = request.session.get('guest_email_id')
    #
    # user = request.user
    # billing_profile = None
    #
    # if user.is_authenticated:
    #     # logged in user checking; remember payment stuff
    #     billing_profile, billing_profile_created = BillingProfile.objects.get_or_create(user=user, email=user.email)
    #     # print(billing_profile)
    # elif guest_email_id is not None:
    #     # guest user checkout; auto reloads payment stuff
    #     guest_email_obj = GuestEmail.objects.get(id=guest_email_id)
    #     billing_profile, billing_profile_created = BillingProfile.objects.get_or_create(email=guest_email_obj.email)
    # else:
    #     pass
    # print("Reached???")
    address_qs = None
    has_card = False
    if billing_profile is not None:
        # print('billing_profile=', billing_profile, billing_profile_created)
        if request.user.is_authenticated:
            address_qs = Address.objects.filter(billing_profile=billing_profile)

        # shipping_address_qs = address_qs.filter(address_type='shipping')
        # billing_address_qs = address_qs.filter(address_type='billing')
        order_obj, order_created = Order.objects.new_or_get(billing_profile, cart_obj)
        # print(order_obj, order_created)
        # order_qs = Order.objects.filter(billing_profile=billing_profile, cart=cart_obj, active=True)
        # if order_qs.count() == 1:
        #     order_obj = order_qs.first()
        # else:
        #     # old_order_qs = Order.objects.exclude(billing_profile=billing_profile).filter(cart=cart_obj, active=True)
        #     # if old_order_qs.exists():
        #     #     old_order_qs.update(active=False)
        #     order_obj = Order.objects.create(billing_profile=billing_profile, cart=cart_obj)
        if shipping_address_id:
            # print("Ship add")
            order_obj.shipping_address = Address.objects.get(id=shipping_address_id)
            # del request.session['shipping_address_id']
        if billing_address_id:
            # print('bill add', billing_address_id)
            order_obj.billing_address = Address.objects.get(id=billing_address_id)
            # del request.session['billing_address_id']
        if billing_address_id or shipping_address_id:
            order_obj.save()
        has_card = billing_profile.has_card

        if request.method == "POST":
            # is_done = order_obj.check_done()
            # if is_done:
            #     order_obj.mark_paid()
            #     request.session['cart_items'] = 0
            #     del request.session['cart_id']
            #     return redirect('cart:checkout_success')
            is_prepared = order_obj.check_done()
            # print("prepared: ", is_prepared)
            if is_prepared:
                did_charge, crg_msg = billing_profile.charge(order_obj)
                if did_charge:
                    order_obj.mark_paid()
                    request.session['cart_items'] = 0
                    del request.session['cart_id']
                    if not billing_profile.user:
                        # ''' is this the best spot?'''
                        billing_profile.set_cards_inactive()
                    return redirect("cart:checkout_success")
                else:
                    # print(crg_msg)
                    return redirect("cart:checkout")

    context = {
        'object': order_obj,
        'billing_profile': billing_profile,
        'form': form,
        'guest_form': guest_form,
        'address_form': address_form,
        'address_qs': address_qs,
        # 'billing_address_form': billing_address_form,
        "has_card": has_card,
        "publish_key": STRIPE_PUB_KEY,
    }
    # print(billing_profile)
    # print("Printing Context in Cart Views")
    # print(context)
    return render(request, 'cart/checkout.html', context)


def checkout_done_view(request):
    return render(request, "cart/checkout_done.html", {})
