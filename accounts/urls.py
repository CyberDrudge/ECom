from django.conf.urls import url

from .views import (
        AccountHomeView, AccountEmailActivateView, UserDetailUpdateView
        )
from products.views import UserProductHistoryView

app_name = "accounts"

urlpatterns = [
    url('', AccountHomeView.as_view(), name='home'),
    url('details/', UserDetailUpdateView.as_view(), name='user-update'),
    url('email/confirm/?P<key>[0-9A-Za-z]+', AccountEmailActivateView.as_view(), name='email-activate'),
    url('email/resend-activation/', AccountEmailActivateView.as_view(), name='resend-activation'),
    url('history/products/', UserProductHistoryView.as_view(), name='user-product-history'),

]
