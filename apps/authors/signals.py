from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.authors.models import Author
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=Author)
def sync_author_with_user(sender, instance, **kwargs):
    """Author modeli o'zgartirilganda User modelini ham yangilaydi."""
    if instance.user:
        user = instance.user
        updated_fields = []

        # Sinxronizatsiya qilinadigan maydonlar
        field_mapping = {
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "email": instance.email,
        }

        # Har bir maydonni tekshirish va yangilash
        for user_field, author_value in field_mapping.items():
            if getattr(user, user_field) != author_value:
                setattr(user, user_field, author_value)
                updated_fields.append(user_field)

        # Agar o'zgarish bo'lsa, user modelini saqlash
        if updated_fields:
            user.save(update_fields=updated_fields)
