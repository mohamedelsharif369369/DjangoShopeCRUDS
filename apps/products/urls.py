from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path(
        "category/<path:path>/",
        views.category_detail,
        name="category_detail",
    ),
    path(
        "",
        views.product_list,
        name="product_list",
    ),
    path(
        "<slug:slug>/",
        views.product_detail,
        name="product_detail",
    ),
]
