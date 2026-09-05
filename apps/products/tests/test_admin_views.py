import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.products.models import Category, Product, InventoryTransaction


class AdminViewsTests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username="staffuser",
            password="test-password-123",
            is_staff=True,
        )

        self.category = Category.objects.create(
            name="Electronics",
            slug="electronics",
        )

        self.product = Product.objects.create(
            name="Admin Test Product",
            slug="admin-test-product",
            sku="ADMIN-001",
            category=self.category,
            price="100.00",
            stock_quantity=10,
            low_stock_threshold=5,
        )

        self.client.force_login(self.user)

    def test_inventory_management_get(self):
        response = self.client.get(
            reverse("inventory_management")
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_inventory_management_stock_in(self):
        response = self.client.post(
            reverse("inventory_management"),
            {
                "product": self.product.pk,
                "transaction_type": "in",
                "quantity": 5,
                "note": "Admin restock",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock_quantity,
            15,
        )

        self.assertEqual(
            InventoryTransaction.objects.filter(
                product=self.product,
                transaction_type="in",
            ).count(),
            1,
        )

    def test_inventory_management_invalid_quantity(self):
        response = self.client.post(
            reverse("inventory_management"),
            {
                "product": self.product.pk,
                "transaction_type": "in",
                "quantity": 0,
                "note": "Invalid",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock_quantity,
            10,
        )

    def test_bulk_inventory_update_get(self):
        response = self.client.get(
            reverse("bulk_inventory_update")
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "products",
            response.context,
        )
        self.assertIn(
            "low_stock_products",
            response.context,
        )

    def test_bulk_inventory_update_stock_in(self):
        second_product = Product.objects.create(
            name="Second Admin Product",
            slug="second-admin-product",
            sku="ADMIN-002",
            category=self.category,
            price="200.00",
            stock_quantity=20,
            low_stock_threshold=5,
        )

        response = self.client.post(
            reverse("bulk_inventory_update"),
            {
                "product_ids": [
                    str(self.product.pk),
                    str(second_product.pk),
                ],
                "transaction_type": "in",
                "quantity": "5",
                "note": "Bulk restock",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.product.refresh_from_db()
        second_product.refresh_from_db()

        self.assertEqual(
            self.product.stock_quantity,
            15,
        )
        self.assertEqual(
            second_product.stock_quantity,
            25,
        )

    def test_bulk_inventory_update_requires_products(self):
        response = self.client.post(
            reverse("bulk_inventory_update"),
            {
                "transaction_type": "in",
                "quantity": "5",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock_quantity,
            10,
        )

    def test_bulk_inventory_update_rejects_invalid_quantity(self):
        response = self.client.post(
            reverse("bulk_inventory_update"),
            {
                "product_ids": [str(self.product.pk)],
                "transaction_type": "in",
                "quantity": "0",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock_quantity,
            10,
        )

    def test_bulk_inventory_low_stock_list(self):
        self.product.stock_quantity = 3
        self.product.save()

        response = self.client.get(
            reverse("bulk_inventory_update")
        )

        self.assertEqual(response.status_code, 200)

        low_stock_products = list(
            response.context["low_stock_products"]
        )

        self.assertIn(
            self.product,
            low_stock_products,
        )

    def test_save_category_order(self):
        phones = Category.objects.create(
            name="Phones",
            slug="phones",
            parent=self.category,
        )

        response = self.client.post(
            reverse("save_category_order"),
            data=json.dumps(
                {
                    "category_ids": [
                        phones.pk,
                        self.category.pk,
                    ]
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertTrue(data["success"])

        self.category.refresh_from_db()
        phones.refresh_from_db()

        self.assertEqual(self.category.order, 2)
        self.assertEqual(phones.order, 1)

    def test_save_category_order_rejects_invalid_list(self):
        response = self.client.post(
            reverse("save_category_order"),
            data=json.dumps(
                {
                    "category_ids": "invalid"
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

        data = response.json()

        self.assertFalse(data["success"])

    def test_save_category_order_rejects_invalid_json(self):
        response = self.client.post(
            reverse("save_category_order"),
            data="{invalid-json",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

        data = response.json()

        self.assertFalse(data["success"])

    def test_non_staff_cannot_access_inventory(self):
        self.client.logout()

        User = get_user_model()

        normal_user = User.objects.create_user(
            username="normaluser",
            password="test-password-123",
        )

        self.client.force_login(normal_user)

        response = self.client.get(
            reverse("inventory_management")
        )

        self.assertEqual(response.status_code, 302)
