import datetime
import re

from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Order


CARD_TYPES = (
    ('Mastercard','Mastercard'),
    ('VISA','VISA'),
    ('AMEX','AMEX'),
)

LOCATIONS = (
    ('',''),
    ('Algonquin','Algonquin'),
    ('Lasalle','Lasalle'),
)

def cc_expire_years():
    current_year = datetime.datetime.now().year
    years = range(current_year, current_year + 12)
    return [(str(x),str(x)) for x in years]

def cc_expire_months():
    months = []
    for month in range(1,13):
        if len(str(month)) == 1:
            numeric = '0' + str(month)
        else:
            numeric = str(month)
        months.append((numeric, datetime.date(2011, month, 1).strftime('%B')))
    return months

def strip_non_numbers(data):
    """
    Gets rid of all non-number character
    """
    non_numbers = re.compile('\D')
    return non_numbers.sub('', data)

def cardLuhnChecksumIsValid(card_number):
    """
    Gateway test credit cards won't pass this validation.
    Checks to make sure that the card passes a luhn mod-10 checksum
    """
    sum = 0
    num_digits = len(card_number)
    oddeven = num_digits & 1
    for count in range(0, num_digits):
        digit = int(card_number[count])
        if not ((count & 1) ^ oddeven):
            digit = digit * 2
        if digit > 9:
            digit = digit - 9
        sum = sum + digit
    return ((sum % 10) == 0)
    

class CheckoutForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CheckoutForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['size'] = '30'
            self.fields['billing_state_province'].widget.attrs['size'] = '3'
            self.fields['billing_zip_postal'].widget.attrs['size'] = '6'
            self.fields['credit_card_type'].widget.attrs['size'] = '1'
            self.fields['credit_card_expire_year'].widget.attrs['size'] = '1'
            self.fields['credit_card_expire_month'].widget.attrs['size'] = '1'
            self.fields['credit_card_cvv'].widget.attrs['size'] = '5'
            self.fields['location'].widget.attrs['size'] = '1'
    
    class Meta:
        model = Order
        exclude = ('status', 'ip_address', 'user', 'transaction_id', 'last_updated', 'date')
    
    location = forms.CharField(widget=forms.Select(choices=LOCATIONS), required=False)
    credit_card_number = forms.CharField(required=False)
    credit_card_type = forms.CharField(widget=forms.Select(choices=CARD_TYPES), required=False)
    credit_card_expire_month = forms.CharField(required=False, widget=forms.Select(choices=cc_expire_months()))
    credit_card_expire_year = forms.CharField(required=False, widget=forms.Select(choices=cc_expire_years()))
    credit_card_cvv = forms.CharField(required=False)
    
    def clean_credit_card_number(self):
        cc_number = self.cleaned_data['credit_card_number']
        stripped_cc_number = strip_non_numbers(cc_number)
        if not cardLuhnChecksumIsValid(stripped_cc_number):
            raise forms.ValidationError(_('The credit card you entered is invalid.'))

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        stripped_phone = strip_non_numbers(phone)
        if len(stripped_phone) < 10:
            raise forms.ValidationError(_('Enter a valid phone number with area code.(e.g.555-555-5555)'))
        return self.cleaned_data['phone']