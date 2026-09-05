from django.test import TestCase
from django.urls import reverse

from apps.products.models import Category, Product, Tag


class ProductViewsTests(TestCase):
    def setUp(self):
        self.electronics = Category.objects.create(
            name="Electronics",
            slug="electronics",
        )
        self.phones = Category.objects.create(
            name="Phones",
            slug="phones",
            parent=self.electronics,
        )
        self.smartphones = Category.objects.create(
            name="Smartphones",
            slug="smartphones",
            parent=self.phones,
        )

        self.tag = Tag.objects.create(
            name="Featured",
            slug="featured",
        )

        self.product = Product.objects.create(
            name="iPhone Test",
            slug="iphone-test",
            sku="IPHONE-TEST-001",
            description="Premium smartphone for testing search.",
            category=self.smartphones,
            price="999.00",
            stock_quantity=20,
            is_active=True,
        )
        self.product.tags.add(self.tag)

        self.inactive_product = Product.objects.create(
            name="Inactive Product",
            slug="inactive-product",
            sku="INACTIVE-001",
            description="This product is inactive.",
            category=self.smartphones,
            price="100.00",
            is_active=False,
        )

    def test_product_list_loads(self):
        response = self.client.get(
            reverse("products:product_list")
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["page_obj"].paginator.count,
            1,
        )

    def test_product_list_search_by_name(self):
        response = self.client.get(
            reverse("products:product_list"),
            {"q": "iPhone Test"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["page_obj"].paginator.count,
            1,
        )
        self.assertEqual(
            response.context["page_obj"].object_list[0],
            self.product,
        )

    def test_product_list_search_by_sku(self):
        response = self.client.get(
            reverse("products:product_list"),
            {"q": "IPHONE-TEST-001"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["page_obj"].paginator.count,
            1,
        )

    def test_product_list_search_by_description(self):
        response = self.client.get(
            reverse("products:product_list"),
            {"q": "Premium smartphone"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["page_obj"].paginator.count,
            1,
        )

    def test_product_list_search_by_category(self):
        response = self.client.get(
            reverse("products:product_list"),
            {"q": "Smartphones"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["page_obj"].paginator.count,
            1,
        )

    def test_product_list_search_by_tag(self):
        response = self.client.get(
            reverse("products:product_list"),
            {"q": "Featured"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["page_obj"].paginator.count,
            1,
        )

    def test_inactive_products_are_hidden(self):
        response = self.client.get(
            reverse("products:product_list")
        )

        products = list(
            response.context["page_obj"].object_list
        )

        self.assertNotIn(
            self.inactive_product,
            products,
        )

    def test_product_list_pagination(self):
        for i in range(20):
            Product.objects.create(
                name=f"Pagination Product {i}",
                slug=f"pagination-product-{i}",
                sku=f"PAG-{i:03d}",
                category=self.smartphones,
                price="100.00",
                is_active=True,
            )

        response = self.client.get(
            reverse("products:product_list")
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["page_obj"].paginator.per_page,
            12,
        )
        self.assertTrue(
            response.context["page_obj"].has_next()
        )

    def test_product_detail_loads(self):
        response = self.client.get(
            reverse(
                "products:product_detail",
                kwargs={"slug": self.product.slug},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["product"],
            self.product,
        )

    def test_inactive_product_detail_returns_404(self):
        response = self.client.get(
            reverse(
                "products:product_detail",
                kwargs={"slug": self.inactive_product.slug},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_missing_product_returns_404(self):
        response = self.client.get(
            reverse(
                "products:product_detail",
                kwargs={"slug": "does-not-exist"},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_category_detail_loads(self):
        response = self.client.get(
            reverse(
                "products:category_detail",
                kwargs={"path": "electronics/phones/smartphones"},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["category"],
            self.smartphones,
        )
        self.assertEqual(
            len(response.context["breadcrumbs"]),
            3,
        )
        self.assertEqual(
            response.context["page_obj"].paginator.count,
            1,
        )

    def test_invalid_category_path_returns_404(self):
        response = self.client.get(
            reverse(
                "products:category_detail",
                kwargs={"path": "electronics/wrong/smartphones"},
            )
        )

        self.assertEqual(response.status_code, 404)
