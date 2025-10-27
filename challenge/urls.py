from django.urls import path
from . import views

urlpatterns = [
    path('product/', views.ProductAPIView.as_view(), name='product-post'),
    path('product/<str:id>/', views.ProductAPIView.as_view(), name='product-get'),
]
