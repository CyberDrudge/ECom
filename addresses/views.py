from django.shortcuts import render, redirect
from django.utils.http import is_safe_url
from django.urls import reverse
from django.views.generic import UpdateView, ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import AddressForm, AddressCheckoutForm
from .models import Address
from billing.models import BillingProfile
from utility.helper import response_format

# Create your views here.
# def checkout_address_create_view(request):
#     form = AddressCheckoutForm(request.POST or None)
#     context = {
#         'form': form
#     }
#     next_ = request.GET.get('next')
#     next_post = request.POST.get('next')
#     redirect_path = next_ or next_post or None
#     if form.is_valid():
#         # print(form.cleaned_data)
#         # print(request.POST)
#         instance = form.save(commit=False)
#         billing_profile, billing_created = BillingProfile.objects.new_or_get(request)

#         if billing_profile:
#             address_type = request.POST.get('address_type', 'shipping')
#             instance.billing_profile = billing_profile
#             instance.address_type = request.POST.get('address_type', 'shipping')
#             instance.save()
#             request.session[address_type+'_address_id'] = instance.id
#             # print(address_type+'_address_id')
#         else:
#             # print("Error at addresses views")
#             return redirect("cart:checkout")

#         if is_safe_url(redirect_path, request.get_host()):
#             return redirect(redirect_path)
#         else:
#             return redirect("cart:checkout")
#     return redirect("cart:checkout")


class AddressCreateAPIView(APIView):

    def post(self, request):
        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None
        data = request.data
        form = AddressCheckoutForm(data or None)
        instance = form.save(commit=False)
        billing_profile, billing_created = BillingProfile.objects.new_or_get(request)
        if billing_profile:
            address_type = request.POST.get('address_type', 'shipping')
            instance.billing_profile = billing_profile
            instance.address_type = address_type
            instance.save()
            # request.session[address_type+'_address_id'] = instance.id
        else:
            print("Error at addresses views")
            return redirect("   cart:checkout")
        message = "Address Added. Redirect to Checkout"
        context = response_format(success=True, message=message)
        return Response(context, status.HTTP_200_OK)


def checkout_address_reuse_view(request):
    if request.user.is_authenticated:
        context = {}
        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None
        if request.method == "POST":
            # print(form.cleaned_data)
            # print(request.POST)
            billing_profile, billing_created = BillingProfile.objects.new_or_get(request)
            shipping_address = request.POST.get('shipping_address', None)
            address_type = request.POST.get('address_type', 'shipping')
            if shipping_address is not None:
                qs = Address.objects.filter(billing_profile=billing_profile, id=shipping_address)
                if qs.exists():
                    request.session[address_type+'_address_id'] = shipping_address
            # print(address_type+'_address_id')

            if is_safe_url(redirect_path, request.get_host()):
                return redirect(redirect_path)
            else:
                return redirect("cart:checkout")
    return redirect("cart:checkout")


def show_addresses_view(request):
    if request.user.is_authenticated:
        template_name = 'addresses/show_addresses.html'
        billing_profile, billing_created = BillingProfile.objects.new_or_get(request)
        queryset = Address.objects.filter(billing_profile=billing_profile)
        context = {
            'object_list': queryset
        }
        return render(request, template_name, context)
    else:
        return redirect("login")


class AddressEditView(UpdateView):
    form_class = AddressForm
    template_name = 'addresses/address_edit.html'

    def get_object(self, *args, **kwargs):
        request = self.request
        pk = self.kwargs.get('pk')
        instance = Address.objects.filter(id=pk).first()
        return instance

    def get_context_data(self, *args, **kwargs):
        context = super(AddressEditView, self).get_context_data(*args, **kwargs)
        context['title'] = 'Edit Your Address Details'
        return context

    def get_success_url(self):
        return reverse("addresses:show_address")


class AddressListView(LoginRequiredMixin, ListView):
    template_name = 'addresses/list.html'

    def get_queryset(self):
        request = self.request
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        return Address.objects.filter(billing_profile=billing_profile)


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'addresses/update.html'
    form_class = AddressForm
    success_url = '/addresses'

    def get_queryset(self):
        request = self.request
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        return Address.objects.filter(billing_profile=billing_profile)


class AddressCreateView(LoginRequiredMixin, CreateView):
    template_name = 'addresses/update.html'
    form_class = AddressForm
    success_url = '/addresses'

    def form_valid(self, form):
        request = self.request
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        instance = form.save(commit=False)
        instance.billing_profile = billing_profile
        instance.save()
        return super(AddressCreateView, self).form_valid(form)
