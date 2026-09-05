from django.contrib import admin
from django.urls import include, path

from apps.products.admin_views import inventory_management, bulk_inventory_update, save_category_order


urlpatterns = [
    path("admin/inventory-management/", inventory_management, name="inventory_management"),
    path("admin/bulk-inventory-update/", bulk_inventory_update, name="bulk_inventory_update"),
    path("admin/save-category-order/", save_category_order, name="save_category_order"),
    path("admin/", admin.site.urls),
    path("products/", include("apps.products.urls")),
]
