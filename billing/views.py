from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.utils.http import is_safe_url

# import stripe
# stripe.api_key = ""
# STRIPE_PUB_KEY = ""


# Create your views here.
# def payment_method_view(request):
#     next_url = None
#     next_ = request.GET.get('next')
#     if is_safe_url(next_, request.get_host()):
#         next_url = next_
#     return render(request, 'billing/payment_method.html', {"pub_key": STRIPE_PUB_KEY, "next_url": next_url})
#
#
# def payment_method_create_view(request):
#     if request.method == "POST":
#         print(request.POST)
#         return JsonResponse({"message": "Done"})
#     return HttpResponse("Error", status_code=401)

