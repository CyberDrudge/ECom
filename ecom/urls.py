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
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView


from products.views import homepage
from accounts.views import LoginView, RegisterView, guest_register_page
from addresses.views import checkout_address_create_view, checkout_address_reuse_view

urlpatterns = [
    path('', homepage, name='home'),
    path('admin/', admin.site.urls),
    path('cart/', include('cart.urls', namespace='cart')),
    path('checkout/address/create/', checkout_address_create_view, name='checkout_address_create'),
    path('checkout/address/reuse/', checkout_address_reuse_view, name='checkout_address_reuse'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('navbar/', TemplateView.as_view(template_name='products/navbar.html')),
    path('products/', include('products.urls', namespace='products'), name='products'),
    path('register/', RegisterView.as_view(), name='register'),
    path('register/guest/', guest_register_page, name='guest_register'),
    path('search/', include('search.urls', namespace='search')),
    path('temp/', TemplateView.as_view(template_name='products/test_template.html')),
    # path('products-fbv/', list_view),
    # path('products/', ProductListView.as_view()),
    # path('detail-fbv/<pk>', detail_view),
    # path('detail/<int:pk>', ProductDetailView.as_view()),
    # path('detail/<slug>', ProductSlugDetailView.as_view()),
    # path('featured/', ProductFeaturedListView.as_view()),
    # path('featured-detail/<pk>', ProductFeaturedDetailView.as_view()),
]

# Add products
# Profile
# Address
# product images

