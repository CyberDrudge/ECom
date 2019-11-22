from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save, post_save

from accounts.models import GuestEmail
import stripe
# stripe.api_key = getattr(settings, )

User = settings.AUTH_USER_MODEL


# Create your models here.
class BillingProfileManager(models.Manager):
    def new_or_get(self, request):
        user = request.user
        guest_email_id = request.session.get('guest_email_id')
        created = False
        obj = None
        if user.is_authenticated:
            # logged in user checking; remember payment stuff
            # print(user, user.email)
            obj, created = self.model.objects.get_or_create(user=user, email=user.email)
            # print(obj, created)
        elif guest_email_id is not None:
            # guest user checkout; auto reloads payment stuff
            guest_email_obj = GuestEmail.objects.get(id=guest_email_id)
            obj, created = self.model.objects.get_or_create(
                email=guest_email_obj.email)
        else:
            print("BPM ELSE")
        return obj, created


class BillingProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField()
    active = models.BooleanField(default=True)
    update = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    customer_id = models.CharField(max_length=120, blank=True, null=True)   # Customer id in stripe (or braintree)

    objects = BillingProfileManager()

    def __str__(self):
        return str(self.email)


def user_created_receiver(sender, instance, created, *args, **kwargs):
    if created and instance.email:
        BillingProfile.objects.get_or_create(user=instance, email=instance.email)


post_save.connect(user_created_receiver, sender=User)


def billing_profile_created(sender, instance, *args, **kwargs):
    if not instance.customer_id and instance.email:
        print("ACTUAL API REQUEST Send to stripe")
        customer = stripe.Customer.create(email=instance.email)
        instance.customer_id = customer.id
        print(customer)


pre_save.connect(billing_profile_created, sender=BillingProfile)
