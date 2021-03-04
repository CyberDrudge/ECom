from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save, post_save

from coupons.models import Coupon
from products.models import Product

User = settings.AUTH_USER_MODEL


# Create your models here.
class CartManager(models.Manager):
	def new_or_get(self, request, cart_id):
		qs = self.get_queryset().filter(id=cart_id)
		new_obj = False
		if qs.count() == 1:
			cart_obj = qs.first()
			if request.user.is_authenticated and cart_obj.user is None:
				cart_obj.user = request.user
				cart_obj.save()
		else:
			new_obj = True
			cart_obj = Cart.objects.new(user=request.user)
			request.session['cart_id'] = cart_obj.id
		return cart_obj, new_obj

	def new(self, user=None):
		user_obj = None
		if user is not None:
			if user.is_authenticated:
				user_obj = user
		return self.model.objects.create(user=user_obj)


class Cart(models.Model):
	user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
	subtotal = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
	total = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
	delivery_charge = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
	coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.CASCADE)
	timestamp = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	objects = CartManager()

	def __str__(self):
		return str(self.id)


class OrderItem(models.Model):
	cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	quantity = models.IntegerField(default=1)
	ordered = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.quantity} of {self.product.title}"

	def get_total_item_price(self):
		return self.quantity * self.product.price

	def get_total_discount_item_price(self):
		return self.quantity * self.product.discount_price

	def get_amount_saved(self):
		return self.get_total_item_price() - self.get_total_discount_item_price()

	def get_final_price(self):
		if self.product.discount_price:
			return self.get_total_discount_item_price()
		return self.get_total_item_price()


def pre_save_cart_receiver(sender, instance, *args, **kwargs):
	instance.total = instance.subtotal
	if instance.total > 5000:
		instance.delivery_charge = 0
	else:
		instance.delivery_charge = 500
	instance.total += instance.delivery_charge
	if instance.coupon:
		instance.total -= instance.coupon.amount
	instance.total = max(instance.total, 0)


pre_save.connect(pre_save_cart_receiver, sender=Cart)


def post_save_order_receiver(sender, instance, *args, **kwargs):
	cart = instance.cart
	cart_items = cart.orderitem_set.all()
	total = sum((item.product.discount_price if item.product.discount_price else item.product.price) * item.quantity for item in cart_items)
	cart.subtotal = total
	cart.save()


post_save.connect(post_save_order_receiver, sender=OrderItem)
