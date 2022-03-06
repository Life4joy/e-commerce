from django.contrib import admin

from .models import *

admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(BillingAddress)
admin.site.register(Category)
admin.site.register(Coupon)
