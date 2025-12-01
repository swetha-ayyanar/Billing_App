from django import forms


class AddProductRow(forms.Form):
    product_id = forms.CharField(max_length=50)
    quantity = forms.IntegerField(min_value=1)


class BillingForm(forms.Form):
    customer_email = forms.EmailField()
    amount_paid = forms.FloatField(min_value=0)
    # product rows will be handled dynamically via JS + POST JSON