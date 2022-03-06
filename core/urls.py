from django.urls import path
from .views import *

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('item/<slug>/', ItemDetail.as_view(), name='item-detail'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('order-summary/', OrderSummary.as_view(), name='order-summary'),
    path('add-coupon/', AddPromoCode.as_view(), name='add-promo-code'),
    path('remove-item-from-cart/<slug>/', minus_item_from_cart, name='remove-item-from-cart'),
    path('add-item-from-cart/<slug>/', plus_item_to_cart, name='add-item-from-cart'),
    path('delete-items-from-cart/<slug>/', delete_items_from_cart, name='delete_items_from_cart'),
    path('checkout/', CheckOut.as_view(), name='checkout'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('filter/<slug:slug>/', Filter.as_view(), name='filter'),
    path('search/', JsonFilterProductsView.as_view(), name='search'),
]
