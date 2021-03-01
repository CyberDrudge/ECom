
from django.urls import path
from .views import (
    ProductListView,
    ProductDetailView,
    ProductSlugDetailView,
    )

app_name = 'products'

urlpatterns = [
    path('', ProductListView.as_view(), name='list'),
    # path('detail-fbv/<pk>', detail_view),
    path('<int:pk>', ProductDetailView.as_view(), name='detail'),
    path('<slug>', ProductSlugDetailView.as_view(), name='detail'),
    # path('featured/', ProductFeaturedListView.as_view()),
    # path('featured-detail/<pk>', ProductFeaturedDetailView.as_view()),
]
