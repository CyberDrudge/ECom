
from django.urls import path
from .views import CouponDetailView

app_name = 'coupons'

urlpatterns = [
    path('', CouponDetailView.as_view(), name='apply-coupon'),
]
