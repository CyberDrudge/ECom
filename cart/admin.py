from django.contrib import admin
from .models import Cart, OrderItem


# Register your models here.
class BookInline(admin.TabularInline):
	model = OrderItem
	extra = 0


class CartAdmin(admin.ModelAdmin):
	inlines = [
		BookInline,
	]


admin.site.register(Cart, CartAdmin)
admin.site.register(OrderItem)
