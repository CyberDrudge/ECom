from django.db import models
from django.db.models.signals import pre_save
from django.urls import reverse
from django.db.models import Q

from ecom.utils import unique_slug_generator


# Create your models here.
class ProductQuerySet(models.query.QuerySet):
    def featured(self):
        return self.filter(featured=True)

    def search(self, query):
        lookups = (Q(title__icontains=query) |
                   Q(description__icontains=query) |
                   Q(price__icontains=query) |
                   Q(tag__title__icontains=query))
        return self.filter(lookups).distinct()


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id)
        if qs.count() == 1:
            return qs.first()
        return None

    def featured(self):
        return self.get_queryset().featured()

    def search(self, query):
        return self.get_queryset().search(query)


class Product(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(blank=True, unique=True)
    description = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=7)
    featured = models.BooleanField(default=False)
    objects = ProductManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # return f'/products/{self.slug}'
        return reverse("products:detail", kwargs={'slug': self.slug})


def product_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(product_pre_save_receiver, sender=Product)


