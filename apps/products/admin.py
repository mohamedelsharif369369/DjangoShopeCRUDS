from django.contrib import admin
from django.db import models
from .models import Category, Tag, Product, InventoryTransaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order", "name")
    change_list_template = "admin/products/category/change_list.html"

    class Media:
        css = {
            "all": ("admin/products/category/category-order.css",)
        }
        js = ("admin/products/category/category-order.js",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    class LowStockFilter(admin.SimpleListFilter):
        title = "Stock status"
        parameter_name = "stock_status"

        def lookups(self, request, model_admin):
            return (
                ("low", "Low stock"),
                ("ok", "Stock OK"),
            )

        def queryset(self, request, queryset):
            if self.value() == "low":
                return queryset.filter(
                    stock_quantity__lte=models.F("low_stock_threshold")
                )
            if self.value() == "ok":
                return queryset.filter(
                    stock_quantity__gt=models.F("low_stock_threshold")
                )
            return queryset

    list_display = (
        "name",
        "sku",
        "category",
        "price",
        "stock_quantity",
        "is_low_stock",
        "is_active",
        "updated_at",
    )

    list_filter = (
        "is_active",
        "category",
        LowStockFilter,
    )

    search_fields = (
        "name",
        "sku",
        "description",
        "tags__name",
        "category__name",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    filter_horizontal = ("tags",)

    list_editable = (
        "price",
        "is_active",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = (
        "product",
        "transaction_type",
        "quantity",
        "note",
        "created_at",
    )

    list_filter = (
        "transaction_type",
        "created_at",
    )

    search_fields = (
        "product__name",
        "product__sku",
        "note",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = ("-created_at",)
