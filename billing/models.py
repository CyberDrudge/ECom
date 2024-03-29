from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save, post_save
from django.shortcuts import reverse
from accounts.models import GuestEmail
import stripe

User = settings.AUTH_USER_MODEL


# Create your models here.
class BillingProfileManager(models.Manager):
    def new_or_get(self, request):
        user = request.user
        # guest_email_id = request.session.get('guest_email_id')
        created = False
        obj = None
        if user.is_authenticated:
            # logged in user checking; remember payment stuff
            # print(user, user.email)
            obj, created = self.model.objects.get_or_create(user=user, email=user.email)
            # print(obj, created)
        # elif guest_email_id is not None:
        #     # guest user checkout; auto reloads payment stuff
        #     guest_email_obj = GuestEmail.objects.get(id=guest_email_id)
        #     obj, created = self.model.objects.get_or_create(
        #         email=guest_email_obj.email)
        # else:
        #     print("BPM ELSE")
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

    def charge(self, order_obj, card=None, token=None):
        return Charge.objects.do(self, order_obj, card=card, token=token)

    def get_cards(self):
        return self.card_set.all()

    def get_payment_method_url(self):
        return reverse('billing_payment_method')

    @property
    def has_card(self):  # instance.has_card
        card_qs = self.get_cards()
        return card_qs.exists()  # True or False

    @property
    def default_card(self):
        default_cards = self.get_cards().filter(active=True, default=True)
        if default_cards.exists():
            return default_cards.first()
        return None

    def set_cards_inactive(self):
        cards_qs = self.get_cards()
        cards_qs.update(active=False)
        return cards_qs.filter(active=True).count()


def user_created_receiver(sender, instance, created, *args, **kwargs):
    if created and instance.email:
        BillingProfile.objects.get_or_create(user=instance, email=instance.email)


post_save.connect(user_created_receiver, sender=User)


def billing_profile_created(sender, instance, *args, **kwargs):
    if not instance.customer_id and instance.email:
        customer = stripe.Customer.create(email=instance.email)
        instance.customer_id = customer.id


pre_save.connect(billing_profile_created, sender=BillingProfile)


class CardManager(models.Manager):

    def all(self, *args, **kwargs):     # ModelKlass.objects.all() --> ModelKlass.objects.filter(active=True)
        return self.get_queryset().filter(active=True)

    def add_new(self, billing_profile, token):
        if token:
            customer = stripe.Customer.retrieve(billing_profile.customer_id)
            stripe_card_response = customer.sources.create(source=token.get('id', ""))
            new_card = self.model(
                    billing_profile=billing_profile,
                    stripe_id=stripe_card_response.id,
                    brand=stripe_card_response.brand,
                    country=stripe_card_response.country,
                    exp_month=stripe_card_response.exp_month,
                    exp_year=stripe_card_response.exp_year,
                    last4=stripe_card_response.last4
                )
            new_card.save()
            return new_card
        return None


class Card(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, on_delete=models.CASCADE)
    stripe_id = models.CharField(max_length=120)
    brand = models.CharField(max_length=120, null=True, blank=True)
    country = models.CharField(max_length=20, null=True, blank=True)
    exp_month = models.IntegerField(null=True, blank=True)
    exp_year = models.IntegerField(null=True, blank=True)
    last4 = models.CharField(max_length=4, null=True, blank=True)
    default = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    objects = CardManager()

    def __str__(self):
        return "{} {}".format(self.brand, self.last4)


class ChargeManager(models.Manager):
    def do(self, billing_profile, order_obj, card=None, token=None): # Charge.objects.do()
        card_obj = card
        if card_obj is None:
            cards = billing_profile.card_set.filter(default=True) # card_obj.billing_profile
            if cards.exists():
                card_obj = cards.first()
        # XNOTE: Temp fix
        if card_obj is None and token is not None:
            card_obj = Card.objects.add_new(billing_profile=billing_profile, token=token)
        if card_obj is None:
            return False, "No cards available"
        c = stripe.Charge.create(
              amount=int(order_obj.total * 100),  # 39.19 --> 3919
              currency="INR",
              customer=billing_profile.customer_id,
              source=card_obj.stripe_id,
              metadata={"order_id": order_obj.order_id},
            )
        new_charge_obj = self.model(
                billing_profile=billing_profile,
                stripe_id=c.id,
                paid=c.paid,
                refunded=c.refunded,
                outcome=c.outcome,
                outcome_type=c.outcome['type'],
                seller_message=c.outcome.get('seller_message'),
                risk_level=c.outcome.get('risk_level'),
        )
        new_charge_obj.save()
        return new_charge_obj.paid, new_charge_obj.seller_message


class Charge(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, on_delete=models.CASCADE)
    stripe_id = models.CharField(max_length=120)
    paid = models.BooleanField(default=False)
    refunded = models.BooleanField(default=False)
    outcome = models.TextField(null=True, blank=True)
    outcome_type = models.CharField(max_length=120, null=True, blank=True)
    seller_message = models.CharField(max_length=120, null=True, blank=True)
    risk_level = models.CharField(max_length=120, null=True, blank=True)

    objects = ChargeManager()


def new_card_post_save_receiver(sender, instance, created, *args, **kwargs):
    if instance.default:
        billing_profile = instance.billing_profile
        qs = Card.objects.filter(billing_profile=billing_profile).exclude(pk=instance.pk)
        qs.update(default=False)


post_save.connect(new_card_post_save_receiver, sender=Card)
