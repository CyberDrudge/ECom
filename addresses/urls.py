from django.urls import path

from .views import (
    # show_addresses_view, 
    ShowAddressesAPIView,
    AddressEditView
)


app_name = 'addresses'

urlpatterns = [
    # path('', show_addresses_view, name='show_address'),
    path('', ShowAddressesAPIView.as_view(), name='show_address'),
    path('<int:pk>', AddressEditView.as_view(), name='edit'),
]
