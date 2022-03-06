from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from .models import BillingAddress, Coupon


class CheckOutForm(forms.ModelForm):
    PAYMENT_CHOICES = (
        ('S', 'Stripe'),
        ('P', 'PayPal')
    )
    country = CountryField(blank_label='(select country)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }))
    same_billing_address = forms.BooleanField(required=False)
    safe_info = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)

    class Meta:
        model = BillingAddress
        fields = (
            'street_address', 'apartment_address', 'country', 'zip', 'same_billing_address', 'safe_info',
            'payment_option'
        )


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ('code', )
# class CheckOutForm(forms.Form):
#     PAYMENT_CHOICES = (
#         ('S', 'Stripe'),
#         ('P', 'PayPal')
#     )
#     apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
#         'placeholder': 'Apartment or suite'
#     }))
#     country = CountryField(blank_label='(select country)').formfield(
#         widget=CountrySelectWidget(attrs={
#             'class': 'custom-select d-block w-100',
#         })
#     )
#     zip = forms.CharField(widget=forms.TextInput(attrs={
#         'class': 'form-control',
#     }))
#     same_billing_address = forms.BooleanField(required=False)
#     safe_info = forms.BooleanField(required=False)
#     payment_option = forms.ChoiceField(
#         widget=forms.RadioSelect, choices=PAYMENT_CHOICES)
