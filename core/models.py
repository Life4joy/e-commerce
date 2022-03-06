from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django_countries.fields import CountryField


class Category(models.Model):
    title = models.CharField(max_length=20)
    slug = models.SlugField()

    def __str__(self):
        return self.title


class Item(models.Model):
    LABEL_CHOICES = (
        ('P', 'primary'),
        ('S', 'secondary'),
        ('D', 'danger')
    )
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    description = models.TextField(null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('item-detail', kwargs={'slug': self.slug})

    def get_add_to_cart_url(self):
        return reverse('add-to-cart', kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse('remove-from-cart', kwargs={'slug': self.slug})


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.item.title

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_price(self):
        return self.quantity * self.item.discount_price

    def get_saving_price(self):
        return self.get_total_item_price() - self.get_total_discount_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(auto_now=True)
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey('BillingAddress', on_delete=models.SET_NULL, blank=True, null=True)
    coupon_code = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon_code:
            total -= self.coupon_code.amount
        return total


class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=30)
    amount = models.FloatField()

    def __str__(self):
        return self.code
