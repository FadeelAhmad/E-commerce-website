from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('order/<int:product_id>/', views.place_order, name='place_order'),
    path('payment/<int:order_id>/', views.process_payment, name='process_payment'),
]
