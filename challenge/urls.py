from django.urls import path
from . import views

urlpatterns = [
    path('product/', views.ProductPostAPIView.as_view(), name='product-post'),
]
