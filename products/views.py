from django.shortcuts import render, get_object_or_404, Http404
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
# from django.views.decorators.cache import cache_page

from .models import Product
from analytics.signals import object_viewed_signal
from analytics.mixin import ObjectViewedMixin
from cart.models import Cart


# Create your views here.
def homepage(request):
    return render(request, 'products/base.html', {})


class ProductListView(ListView):
    template_name = 'products/list_view.html'
    # queryset = Product.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super(ProductListView, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        return context

    def get_queryset(self):
        return Product.objects.all()


CACHE_TTL = 60*15


# @cache_page(CACHE_TTL)
def list_view(request):
    template_name = 'products/list_view.html'
    queryset = Product.objects.all()
    context = {
        'object_list': queryset
    }
    return render(request, template_name, context)


class ProductDetailView(ObjectViewedMixin, DetailView):
    template_name = 'products/detail_view.html'
    # queryset = Product.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
        # print(context)
        return context

    def get_object(self, *args, **kwargs):
        request = self.request
        pk = self.kwargs.get('pk')
        instance = Product.objects.get_by_id(pk)
        if instance is None:
            raise Http404("Product doesn't Exist")
        return instance


class ProductFeaturedListView(ListView):
    template_name = 'products/list_view.html'

    def get_queryset(self):
        return Product.objects.featured()


class ProductFeaturedDetailView(DetailView):
    template_name = 'products/detail_view.html'
    # queryset = Product.objects.all()

    def get_queryset(self):
        return Product.objects.featured()


class ProductSlugDetailView(ObjectViewedMixin, DetailView):
    template_name = 'products/detail_view.html'
    # queryset = Product.objects.all()

    def get_context_data(self, *args, **kwargs):
        request = self.request
        context = super(ProductSlugDetailView, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        context['cart'] = cart_obj
        # print(context)
        return context

    def get_object(self, *args, **kwargs):
        request = self.request
        slug = self.kwargs.get('slug')
        # instance = get_object_or_404(Product, slug=slug)
        try:
            instance = Product.objects.get(slug=slug)
        except Product.DoesNotExist:
            raise Http404("Product doesn't Exist")
        except Product.MultipleObjectsReturned:
            qs = Product.objects.filter(slug=slug)
            instance = qs.first()
        except:
            raise Http404("Ummmmm ... ")

        # object_viewed_signal.send(instance.__class__, instance=instance, request=request)
        return instance


class UserProductHistoryView(LoginRequiredMixin, ListView):
    template_name = "products/user-history.html"

    def get_queryset(self, *args, **kwargs):
        request = self.request
        # views = request.user.objectviewed_set.by_model(Product)  # .all().filter(content_type__name='product')
        # viewed_ids = [x.object_id for x in views]
        # print(viewed_ids)
        # Products.objects.filter(pk__in=viewed_ids)
        x = request.user.objectviewed_set
        # print(x)
        views = request.user.objectviewed_set.by_model(Product, model_queryset=False)
        # print(views)
        return views

