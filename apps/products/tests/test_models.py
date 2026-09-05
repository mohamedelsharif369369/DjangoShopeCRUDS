from django.db import IntegrityError
from django.test import TestCase

from apps.products.models import (
    Category,
    InventoryTransaction,
    Product,
    Tag,
)


class CategoryModelTests(TestCase):

    def test_category_full_path(self):
        electronics = Category.objects.create(
            name="Electronics",
            slug="electronics",
        )
        phones = Category.objects.create(
            name="Phones",
            slug="phones",
            parent=electronics,
        )
        smartphones = Category.objects.create(
            name="Smartphones",
            slug="smartphones",
            parent=phones,
        )

        self.assertEqual(
            electronics.get_full_path(),
            "electronics",
        )
        self.assertEqual(
            phones.get_full_path(),
            "electronics/phones",
        )
        self.assertEqual(
            smartphones.get_full_path(),
            "electronics/phones/smartphones",
        )

    def test_category_slug_unique_per_parent(self):
        parent = Category.objects.create(
            name="Electronics",
            slug="electronics",
        )

        Category.objects.create(
            name="Phones",
            slug="phones",
            parent=parent,
        )

        with self.assertRaises(IntegrityError):
            Category.objects.create(
                name="Other Phones",
                slug="phones",
                parent=parent,
            )

    def test_category_absolute_url(self):
        category = Category.objects.create(
            name="Electronics",
            slug="electronics",
        )

        self.assertEqual(
            category.get_absolute_url(),
            "/products/category/electronics/",
        )


class TagModelTests(TestCase):

    def test_tag_creation(self):
        tag = Tag.objects.create(
            name="Featured",
            slug="featured",
        )

        self.assertEqual(str(tag), "Featured")
        self.assertEqual(tag.slug, "featured")


class ProductModelTests(TestCase):

    def setUp(self):
        self.category = Category.objects.create(
            name="Electronics",
            slug="electronics",
        )

    def test_product_low_stock_property(self):
        product = Product.objects.create(
            name="Test Product",
            slug="test-product",
            sku="TEST-001",
            category=self.category,
            price="100.00",
            stock_quantity=5,
            low_stock_threshold=5,
        )

        self.assertTrue(product.is_low_stock)

        product.stock_quantity = 6
        product.save()

        product.refresh_from_db()

        self.assertFalse(product.is_low_stock)

    def test_product_absolute_url(self):
        product = Product.objects.create(
            name="Test Product",
            slug="test-product",
            sku="TEST-002",
            category=self.category,
            price="100.00",
        )

        self.assertEqual(
            product.get_absolute_url(),
            "/products/test-product/",
        )


class InventoryTransactionModelTests(TestCase):

    def test_inventory_transaction_string(self):
        category = Category.objects.create(
            name="Electronics",
            slug="electronics",
        )

        product = Product.objects.create(
            name="Test Product",
            slug="test-product-transaction",
            sku="TEST-003",
            category=category,
            price="100.00",
        )

        transaction = InventoryTransaction.objects.create(
            product=product,
            transaction_type="in",
            quantity=10,
            note="Test stock",
        )

        self.assertEqual(
            str(transaction),
            "TEST-003 - in - 10",
        )
