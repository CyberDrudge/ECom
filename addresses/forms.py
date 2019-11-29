from django import forms

from .models import Address


class AddressForm(forms.ModelForm):
    """
    User-related CRUD form
    """
    class Meta:
        model = Address
        fields = [
            'nickname',
            'name',
            'address_type',
            'address_line1',
            'address_line2',
            'city',
            'country',
            'state',
            'postal_code',
        ]


class AddressCheckoutForm(forms.ModelForm):
    """
    User-related checkout address create form
    """
    class Meta:
        model = Address
        fields = [
            'nickname',
            'name',
            'address_line1',
            'address_line2',
            'city',
            'country',
            'state',
            'postal_code'
        ]
