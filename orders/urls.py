from django.conf.urls import url
from django.urls import path
from .views import (
        OrderListView,
        OrderDetailView,
        PlaceOrderAPIView
        )

app_name = 'orders'

urlpatterns = [
    url(r'^$', OrderListView.as_view(), name='list'),
    url(r'^(?P<order_id>[0-9A-Za-z]+)/$', OrderDetailView.as_view(), name='detail'),
    path('place-order', PlaceOrderAPIView.as_view(), name='placeorder')
]
