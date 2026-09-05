from django.core.paginator import Paginator
from django.db.models import F
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
)

from .models import Category, Product


def product_list(request):
    products = (
        Product.objects
        .select_related("category")
        .prefetch_related("tags")
        .filter(is_active=True)
    )

    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()

    if query:
        search_query = SearchQuery(
            query,
            search_type="websearch",
            config="simple",
        )

        products = (
            products
            .annotate(
                search_rank=SearchRank(
                    F("search_vector"),
                    search_query,
                ),
            )
            .filter(search_vector=search_query)
            .order_by("-search_rank", "-created_at")
        )

    if category_slug:
        products = products.filter(
            category__slug=category_slug
        )

    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(
        is_active=True
    )

    context = {
        "page_obj": page_obj,
        "categories": categories,
        "query": query,
        "selected_category": category_slug,
    }

    return render(
        request,
        "products/product_list.html",
        context,
    )


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects
        .select_related("category")
        .prefetch_related("tags"),
        slug=slug,
        is_active=True,
    )

    return render(
        request,
        "products/product_detail.html",
        {"product": product},
    )


def category_detail(request, path):
    category = get_object_or_404(
        Category.objects.filter(is_active=True),
        slug=path.rstrip("/").split("/")[-1],
    )

    if category.get_full_path() != path.rstrip("/"):
        raise Http404(
            "Category path does not match the category hierarchy."
        )

    products = (
        Product.objects
        .select_related("category")
        .filter(
            category=category,
            is_active=True,
        )
    )

    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    breadcrumbs = []
    current = category

    while current is not None:
        breadcrumbs.append(current)
        current = current.parent

    breadcrumbs.reverse()

    return render(
        request,
        "products/category_detail.html",
        {
            "category": category,
            "page_obj": page_obj,
            "breadcrumbs": breadcrumbs,
        },
    )
