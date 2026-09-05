from django import forms

from .models import Product


class InventoryTransactionForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True).order_by("name"),
        label="Product",
    )
    transaction_type = forms.ChoiceField(
        choices=[
            ("opening", "Opening Balance"),
            ("in", "Stock In"),
            ("out", "Stock Out"),
            ("adjustment", "Adjustment"),
        ],
        label="Transaction Type",
    )
    quantity = forms.IntegerField(
        min_value=1,
        label="Quantity",
    )
    note = forms.CharField(
        max_length=255,
        required=False,
        label="Note",
        widget=forms.TextInput(),
    )


class BulkInventoryUpdateForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True).order_by("name"),
        label="Product",
    )
    transaction_type = forms.ChoiceField(
        choices=[
            ("in", "Stock In"),
            ("out", "Stock Out"),
            ("adjustment", "Adjustment"),
        ],
        label="Transaction Type",
    )
    quantity = forms.IntegerField(
        min_value=1,
        label="Quantity",
    )
    note = forms.CharField(
        max_length=255,
        required=False,
        label="Note",
        widget=forms.TextInput(),
    )
