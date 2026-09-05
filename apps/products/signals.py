from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Product
from .services.search import update_product_search_vector


@receiver(post_save, sender=Product)
def update_product_search_vector_on_save(sender, instance, **kwargs):
    update_product_search_vector(instance.pk)


from django.db.models.signals import m2m_changed


@receiver(m2m_changed, sender=Product.tags.through)
def update_product_search_vector_on_tags_change(
    sender,
    instance,
    action,
    **kwargs,
):
    if action in {"post_add", "post_remove", "post_clear"}:
        update_product_search_vector(instance.pk)
