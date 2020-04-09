from django.db import models
from django.urls import reverse

from billing.models import BillingProfile

ADDRESS_TYPE = (
    ('billing', 'Billing address'),
    ('shipping', 'Shipping address',)
)


# Create your models here.
class Address(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=120, null=True, blank=True)
    nickname = models.CharField(max_length=120, null=True, blank=True)
    address_type = models.CharField(max_length=120, choices=ADDRESS_TYPE)
    address_line1 = models.CharField(max_length=120)
    address_line2 = models.CharField(max_length=120, null=True, blank=True)
    city = models.CharField(max_length=120)
    country = models.CharField(max_length=120, default='IN')
    state = models.CharField(max_length=120)
    postal_code = models.CharField(max_length=120)

    def __str__(self):
        if self.nickname:
            return str(self.nickname)
        return str(self.address_line1)

    def get_absolute_url(self):
        return reverse("address-update", kwargs={"pk": self.pk})

    def get_short_address(self):
        for_name = self.name
        if self.nickname:
            for_name = "{} | {},".format(self.nickname, for_name)
        return "{for_name} {line1}, {city}".format(
            for_name=for_name or "",
            line1=self.address_line1,
            city=self.city
        )

    def get_address(self):
        return "{for_name}\n{line1}\n{line2}\n{city}\n{state}, {postal}\n{country}".format(
            for_name=self.name or "",
            line1=self.address_line1, line2=self.address_line2 or "",
            city=self.city, state=self.state,
            postal=self.postal_code, country=self.country
        )

    def get_edit_url(self):
        # return f'/addresses/{self.id}'
        return reverse("addresses:edit", kwargs={'pk': self.id})

