from django.db import models


# Create your models here.
class CouponManager(models.Manager):
    def get_by_code(self, code):
        qs = self.get_queryset().filter(code=code)
        if qs.count() == 1:
            return qs.first()
        return None


class Coupon(models.Model):
    code = models.CharField(max_length=120, unique=True)
    amount = models.DecimalField(decimal_places=2, max_digits=7)
    is_active = models.BooleanField(default=True)
    objects = CouponManager()

    def __str__(self):
        return self.code
