from django.contrib import messages
from django.db import models
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .forms import InventoryTransactionForm
from .models import Category, Product
from .services.inventory import create_inventory_transaction


@staff_member_required
def inventory_management(request):
    if request.method == "POST":
        form = InventoryTransactionForm(request.POST)

        if form.is_valid():
            try:
                transaction = create_inventory_transaction(
                    product_id=form.cleaned_data["product"].pk,
                    transaction_type=form.cleaned_data["transaction_type"],
                    quantity=form.cleaned_data["quantity"],
                    note=form.cleaned_data["note"],
                )

                messages.success(
                    request,
                    f"Inventory updated successfully for {transaction.product.sku}.",
                )
                return redirect("inventory_management")

            except Exception as exc:
                form.add_error(None, str(exc))
    else:
        form = InventoryTransactionForm()

    return render(
        request,
        "admin/products/inventory_management.html",
        {"form": form},
    )


@staff_member_required
def bulk_inventory_update(request):
    if request.method == "POST":
        product_ids = request.POST.getlist("product_ids")
        transaction_type = request.POST.get("transaction_type")
        quantity = request.POST.get("quantity")
        note = request.POST.get("note", "").strip()

        if not product_ids:
            messages.error(
                request,
                "Please select at least one product.",
            )
            return redirect("bulk_inventory_update")

        try:
            quantity = int(quantity)

            if quantity <= 0:
                raise ValueError

        except (TypeError, ValueError):
            messages.error(
                request,
                "Quantity must be greater than zero.",
            )
            return redirect("bulk_inventory_update")

        success_count = 0

        for product_id in product_ids:
            try:
                create_inventory_transaction(
                    product_id=product_id,
                    transaction_type=transaction_type,
                    quantity=quantity,
                    note=note,
                )
                success_count += 1

            except Exception as exc:
                messages.error(
                    request,
                    f"Product {product_id}: {exc}",
                )

        if success_count:
            messages.success(
                request,
                f"Inventory updated for {success_count} product(s).",
            )

        return redirect("bulk_inventory_update")

    products = (
        Product.objects
        .filter(is_active=True)
        .order_by("name")
    )

    low_stock_products = (
        Product.objects
        .filter(
            is_active=True,
            stock_quantity__lte=models.F("low_stock_threshold"),
        )
        .order_by("stock_quantity", "name")
    )

    return render(
        request,
        "admin/products/bulk_inventory_update.html",
        {
            "products": products,
            "low_stock_products": low_stock_products,
        },
    )


@staff_member_required
@require_POST
def save_category_order(request):
    import json

    try:
        data = json.loads(request.body)
        category_ids = data.get("category_ids", [])

        if not isinstance(category_ids, list):
            return JsonResponse(
                {"success": False, "error": "Invalid category list."},
                status=400,
            )

        categories = {
            str(category.pk): category
            for category in Category.objects.filter(pk__in=category_ids)
        }

        for order, category_id in enumerate(category_ids, start=1):
            category = categories.get(str(category_id))

            if category is not None:
                category.order = order
                category.save(update_fields=["order"])

        return JsonResponse({"success": True})

    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse(
            {"success": False, "error": "Invalid request."},
            status=400,
        )
