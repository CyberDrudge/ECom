from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.utils.http import is_safe_url
from django.conf import settings
import stripe
from .models import BillingProfile, Card

stripe.api_key = getattr(settings, 'STRIPE_API_KEY')
STRIPE_PUB_KEY = getattr(settings, 'STRIPE_PUB_KEY')


# Create your views here.
def payment_method_view(request):
    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    if not billing_profile:
        return redirect("/cart")
    next_url = None
    next_ = request.GET.get('next')
    if is_safe_url(next_, request.get_host()):
        next_url = next_
    return render(request, 'billing/payment-method.html', {"publish_key": STRIPE_PUB_KEY, "next_url": next_url})


def payment_method_create_view(request):
    if request.method == "POST":
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        if not billing_profile:
            return HttpResponse({"message": "Cannot find this user"}, status_code=401)
        token = request.POST.get("token")
        if token is not None:
            new_card_obj = Card.objects.add_new(billing_profile, token)
            # print(new_card_obj)  # start saving our cards too!
        return JsonResponse({"message": "Success! Your card was added."})
    return HttpResponse("Error", status_code=401)

