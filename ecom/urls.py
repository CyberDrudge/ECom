"""ecom URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.views import LogoutView

from django.conf import settings
from django.conf.urls.static import static

from accounts.views import LoginView, RegisterView, GuestRegisterView
from addresses.views import checkout_address_create_view, checkout_address_reuse_view
# from billing.views import payment_method_view, payment_method_create_view
from products.views import homepage


urlpatterns = [
    path('', homepage, name='home'),
    path('admin/', admin.site.urls),
    # path('about/',),
    path('account/', include('accounts.urls', namespace='account')),
    # path('accounts/', RedirectView.as_view(url='/account')),
    path('accounts/', include("accounts.passwords.urls")),
    # path('billing/payment_method/', payment_method_view, name='billing_payment_method'),
    # path('billing/payment_method/create', payment_method_create_view, name='billing_payment_method_endpoint'),
    path('cart/', include('cart.urls', namespace='cart')),
    path('checkout/address/create/', checkout_address_create_view, name='checkout_address_create'),
    path('checkout/address/reuse/', checkout_address_reuse_view, name='checkout_address_reuse'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('navbar/', TemplateView.as_view(template_name='products/navbar.html')),
    path('orders/', include("orders.urls", namespace='orders')),
    path('products/', include('products.urls', namespace='products'), name='products'),
    path('register/', RegisterView.as_view(), name='register'),
    path('register/guest/', GuestRegisterView.as_view(), name='guest_register'),
    path('search/', include('search.urls', namespace='search')),
    path('temp/', TemplateView.as_view(template_name='products/test_template.html')),
    # path('products-fbv/', list_view),
    # path('products/', ProductListView.as_view()),
    # path('detail-fbv/<pk>', detail_view),
    # path('detail/<int:pk>', ProductDetailView.as_view()),
    # path('detail/<slug>', ProductSlugDetailView.as_view()),
    # path('featured/', ProductFeaturedListView.as_view()),
    # path('featured-detail/<pk>', ProductFeaturedDetailView.as_view()),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Add products
# Profile
# Address
# product images

