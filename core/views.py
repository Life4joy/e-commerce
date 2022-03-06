from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import CheckOutForm, CouponForm
from .models import *
from django.views.generic import ListView, DetailView, View


class Home(ListView):
    model = Item
    template_name = 'home-page.html'
    paginate_by = 2

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()[:3]
        return context


class Filter(ListView):
    model = Item
    template_name = 'filter-page.html'
    paginate_by = 2

    def get_queryset(self, *args, **kwargs):
        items = Item.objects.filter(category__slug=self.kwargs['slug'])
        return items

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()[:3]
        return context


class ItemDetail(DetailView):
    model = Item
    template_name = 'product-page.html'


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


class JsonFilterProductsView(View):
    def get(self, *args, **kwargs):
        if is_ajax(self.request):
            item = self.request.GET.get('item')
            qs = Item.objects.filter(title__icontains=item)
            if len(qs) > 0 and len(item) > 0:
                data = []
                for pos in qs:
                    if pos.discount_price:
                        price = pos.discount_price
                    else:
                        price = pos.price
                    item = {
                        'pk': pos.pk,
                        'title': pos.title,
                        'get_absolute_url': pos.get_absolute_url(),
                        'category': pos.category.title,
                        'get_label_display': pos.get_label_display(),
                        'price': price,
                    }
                    data.append(item)
                res = data
            else:
                res = 'No item found...'
            return JsonResponse({'data': res})
        return JsonResponse({})


class OrderSummary(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order,
            }
            return render(self.request, 'order-summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, 'You do not have an active order')
            return redirect('/')


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, f'The item quantity is {order_item.quantity}')
            return redirect('item-detail', slug=slug)
        else:
            order.items.add(order_item)
            messages.info(request, 'The item was added to your cart')
            return redirect('item-detail', slug=slug)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, 'The item was added to your cart')
        return redirect('item-detail', slug=slug)


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            order_item.quantity = 0
            order_item.save()
            order.items.remove(order_item)
            messages.info(request, 'The item was removed from your cart')
            return redirect('item-detail', slug=slug)
        else:
            # if order doesn't contain the item
            messages.info(request, 'The item was not in your cart')
            return redirect('item-detail', slug=slug)
    else:
        # if user doesn't have an order
        messages.info(request, 'You do not have an active order')
        return redirect('item-detail', slug=slug)


@login_required
def minus_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            if order_item.quantity == 1:
                order.items.remove(order_item)
                messages.info(request, 'The item was removed from your cart')
                return redirect('order-summary')
            else:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, 'The item quantity was updated')
                return redirect('order-summary')
    else:
        # if user doesn't have an order
        messages.info(request, 'You do not have an active order')
        return redirect('item-detail', slug=slug)


@login_required
def plus_item_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            order_item.quantity += 1
            order_item.save()
            messages.info(request, 'The item quantity was updated')
            return redirect('order-summary')
    else:
        # if user doesn't have an order
        messages.info(request, 'You do not have an active order')
        return redirect('item-detail', slug=slug)


@login_required
def delete_items_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            order.items.remove(order_item)
            messages.info(request, 'The item was removed')
            return redirect('order-summary')
    else:
        # if user doesn't have an order
        messages.info(request, 'You do not have an active order')
        return redirect('item-detail', slug=slug)


class CheckOut(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        form = CheckOutForm()
        context = {
            'form': form,
            'order_items': OrderItem.objects.filter(user=self.request.user, ordered=False),
            'order_count': OrderItem.objects.filter(user=self.request.user, ordered=False).count(),
            'order': Order.objects.get(user=self.request.user, ordered=False)
        }
        return render(self.request, 'checkout-page.html', context)

    def post(self, *args, **kwargs):
        form = CheckOutForm(self.request.POST)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                form = form.save(commit=False)
                form.user = self.request.user
                form.country = self.request.POST.get("country")
                form.save()
                order.billing_address = form
                order.save()
                if self.request.POST.get('payment_option') == 'S':
                    return redirect('payment', payment_option='stripe')
                elif self.request.POST.get('payment_option') == 'P':
                    return redirect('payment', payment_option='paypal')
                else:
                    messages.warning(self.request, 'Failed checkout')
                    return redirect('.')
            messages.warning(self.request, 'Failed checkout')
            return redirect('.')
        except ObjectDoesNotExist:
            messages.warning(self.request, 'You do not have an active order')
            return redirect('/')


class PaymentView(View):
    def get(self, *args, **kwargs):
        return render(self.request, 'payment.html')


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.warning(request, 'Code does not exist')
        return None


class AddPromoCode(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user=self.request.user, ordered=False)
                coup_code = get_coupon(self.request, code)
                if coup_code is None:
                    return redirect('checkout')
                else:
                    order.coupon_code = coup_code
                    order.save()
                    messages.success(self.request, 'Successfully added coupon')
                    return redirect('checkout')
            except ObjectDoesNotExist:
                messages.warning(self.request, 'You do not have an active order')
                return redirect('checkout')
