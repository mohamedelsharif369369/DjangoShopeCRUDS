from django.db import connection

from ..models import Product


def update_product_search_vector(product_id):
    product = (
        Product.objects
        .select_related("category")
        .prefetch_related("tags")
        .get(pk=product_id)
    )

    tag_names = " ".join(
        product.tags.values_list("name", flat=True)
    )

    category_name = (
        product.category.name
        if product.category_id
        else ""
    )

    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE products_product
            SET search_vector =
                setweight(
                    to_tsvector(
                        'simple',
                        coalesce(%s, '')
                    ),
                    'A'
                ) ||
                setweight(
                    to_tsvector(
                        'simple',
                        coalesce(%s, '')
                    ),
                    'A'
                ) ||
                setweight(
                    to_tsvector(
                        'simple',
                        coalesce(%s, '')
                    ),
                    'C'
                ) ||
                setweight(
                    to_tsvector(
                        'simple',
                        coalesce(%s, '')
                    ),
                    'B'
                ) ||
                setweight(
                    to_tsvector(
                        'simple',
                        coalesce(%s, '')
                    ),
                    'B'
                )
            WHERE id = %s
            """,
            [
                product.name,
                product.sku,
                product.description,
                category_name,
                tag_names,
                product_id,
            ],
        )
