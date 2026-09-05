from django.core.exceptions import ValidationError
from django.db import transaction

from ..models import InventoryTransaction, Product


@transaction.atomic
def create_inventory_transaction(
    product_id,
    transaction_type,
    quantity,
    note="",
):
    if quantity <= 0:
        raise ValidationError("Quantity must be greater than zero.")

    product = (
        Product.objects
        .select_for_update()
        .get(pk=product_id)
    )

    if transaction_type == "opening":
        if product.stock_quantity != 0:
            raise ValidationError(
                "Opening balance can only be set when current stock is zero."
            )
        product.stock_quantity = quantity

    elif transaction_type == "in":
        product.stock_quantity += quantity

    elif transaction_type == "out":
        if product.stock_quantity < quantity:
            raise ValidationError(
                "Insufficient stock."
            )

        product.stock_quantity -= quantity

    elif transaction_type == "adjustment":
        product.stock_quantity = quantity

    else:
        raise ValidationError(
            "Invalid transaction type."
        )

    product.save(
        update_fields=[
            "stock_quantity",
            "updated_at",
        ]
    )

    return InventoryTransaction.objects.create(
        product=product,
        transaction_type=transaction_type,
        quantity=quantity,
        note=note,
    )
