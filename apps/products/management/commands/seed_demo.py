from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from apps.products.models import Category, Product, Tag


class Command(BaseCommand):
    help = "Create reproducible demo data with 5000 products."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Creating demo data...")

        electronics, _ = Category.objects.get_or_create(
            name="Electronics",
            slug="electronics",
            parent=None,
            defaults={"order": 1, "is_active": True},
        )

        phones, _ = Category.objects.get_or_create(
            name="Phones",
            slug="phones",
            parent=electronics,
            defaults={"order": 2, "is_active": True},
        )

        smartphones, _ = Category.objects.get_or_create(
            name="Smartphones",
            slug="smartphones",
            parent=phones,
            defaults={"order": 3, "is_active": True},
        )

        featured, _ = Tag.objects.get_or_create(
            name="Featured",
            slug="featured",
        )

        demo_tag, _ = Tag.objects.get_or_create(
            name="Demo",
            slug="demo",
        )

        iphone, _ = Product.objects.update_or_create(
            sku="IP17PRO-001",
            defaults={
                "name": "iPhone 17 Pro",
                "slug": "iphone-17-pro",
                "description": "Premium smartphone demo product.",
                "category": smartphones,
                "price": Decimal("4999.00"),
                "stock_quantity": 35,
                "low_stock_threshold": 5,
                "is_active": True,
            },
        )

        iphone.tags.add(featured)

        Product.objects.filter(
            sku__startswith="DEMO-"
        ).delete()

        products_to_create = []

        for number in range(1, 5000):
            if number % 3 == 0:
                category = electronics
            elif number % 3 == 1:
                category = phones
            else:
                category = smartphones

            products_to_create.append(
                Product(
                    name=f"Demo Product {number}",
                    slug=f"demo-product-{number}",
                    sku=f"DEMO-{number:05d}",
                    description=(
                        f"High quality demo product number {number} "
                        "for performance and search testing."
                    ),
                    category=category,
                    price=Decimal(100 + (number % 900)),
                    stock_quantity=50 + (number % 100),
                    low_stock_threshold=5,
                    is_active=True,
                )
            )

        Product.objects.bulk_create(
            products_to_create,
            batch_size=500,
        )

        demo_products = list(
            Product.objects.filter(
                sku__startswith="DEMO-"
            )
        )

        through = Product.tags.through

        through.objects.bulk_create(
            [
                through(
                    product_id=product.pk,
                    tag_id=demo_tag.pk,
                )
                for product in demo_products
            ],
            batch_size=500,
            ignore_conflicts=True,
        )

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE products_product p
                SET search_vector =
                    setweight(
                        to_tsvector(
                            'simple',
                            coalesce(p.name, '')
                        ),
                        'A'
                    ) ||
                    setweight(
                        to_tsvector(
                            'simple',
                            coalesce(p.sku, '')
                        ),
                        'A'
                    ) ||
                    setweight(
                        to_tsvector(
                            'simple',
                            coalesce(p.description, '')
                        ),
                        'C'
                    ) ||
                    setweight(
                        to_tsvector(
                            'simple',
                            coalesce(c.name, '')
                        ),
                        'B'
                    ) ||
                    setweight(
                        to_tsvector(
                            'simple',
                            coalesce(
                                (
                                    SELECT string_agg(t.name, ' ')
                                    FROM products_tag t
                                    JOIN products_product_tags pt
                                        ON pt.tag_id = t.id
                                    WHERE pt.product_id = p.id
                                ),
                                ''
                            )
                        ),
                        'B'
                    )
                FROM products_category c
                WHERE p.category_id = c.id
            """)

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo data ready: {Product.objects.count()} products."
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Search vectors rebuilt successfully."
            )
        )
