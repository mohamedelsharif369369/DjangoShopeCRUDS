from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.products.models import Category, InventoryTransaction, Product
from apps.products.services.inventory import create_inventory_transaction


class InventoryServiceTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Electronics",
            slug="electronics",
        )

        self.product = Product.objects.create(
            name="Test Product",
            slug="test-product-inventory",
            sku="TEST-INV-001",
            category=self.category,
            price="100.00",
            stock_quantity=10,
            low_stock_threshold=5,
        )

    def test_stock_in_increases_stock(self):
        create_inventory_transaction(
            self.product.pk,
            "in",
            5,
            "Restock",
        )

        self.product.refresh_from_db()

        self.assertEqual(self.product.stock_quantity, 15)
        self.assertEqual(
            InventoryTransaction.objects.count(),
            1,
        )

    def test_stock_out_decreases_stock(self):
        create_inventory_transaction(
            self.product.pk,
            "out",
            4,
            "Sale",
        )

        self.product.refresh_from_db()

        self.assertEqual(self.product.stock_quantity, 6)

    def test_stock_out_cannot_exceed_stock(self):
        with self.assertRaises(ValidationError):
            create_inventory_transaction(
                self.product.pk,
                "out",
                11,
                "Too much",
            )

        self.product.refresh_from_db()

        self.assertEqual(self.product.stock_quantity, 10)
        self.assertEqual(
            InventoryTransaction.objects.count(),
            0,
        )

    def test_adjustment_sets_exact_stock(self):
        create_inventory_transaction(
            self.product.pk,
            "adjustment",
            3,
            "Stock count",
        )

        self.product.refresh_from_db()

        self.assertEqual(self.product.stock_quantity, 3)
        self.assertTrue(self.product.is_low_stock)

    def test_opening_balance_requires_zero_stock(self):
        with self.assertRaises(ValidationError):
            create_inventory_transaction(
                self.product.pk,
                "opening",
                20,
                "Opening",
            )

        self.product.refresh_from_db()

        self.assertEqual(self.product.stock_quantity, 10)

    def test_opening_balance_sets_initial_stock(self):
        self.product.stock_quantity = 0
        self.product.save()

        create_inventory_transaction(
            self.product.pk,
            "opening",
            25,
            "Opening",
        )

        self.product.refresh_from_db()

        self.assertEqual(self.product.stock_quantity, 25)

    def test_invalid_transaction_type_is_rejected(self):
        with self.assertRaises(ValidationError):
            create_inventory_transaction(
                self.product.pk,
                "invalid",
                5,
                "Invalid",
            )

        self.product.refresh_from_db()

        self.assertEqual(self.product.stock_quantity, 10)
