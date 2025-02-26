from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.authors.models import Author
from .models import User


@receiver(post_save, sender=User)
def create_author_profile(sender, instance, created, **kwargs):
    """Create an Author profile only when a new User created."""
    if created:
        Author.objects.create(user=instance, email=instance.email)


@receiver(post_save, sender=User)
def sync_user_with_author(sender, instance, **kwargs):
    """User modeli o'zgartirilganda Author modelini ham yangilaydi."""
    try:
        author = instance.profile  # related_name='profile' bo'lgani uchun
        updated_fields = []

        # Sinxronizatsiya qilinadigan maydonlar
        field_mapping = {
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "email": instance.email,
        }

        # Har bir maydonni tekshirish va yangilash
        for author_field, user_value in field_mapping.items():
            if getattr(author, author_field) != user_value:
                setattr(author, author_field, user_value)
                updated_fields.append(author_field)

        # Agar o'zgarish bo'lsa, author modelini saqlash
        if updated_fields:
            author.save(update_fields=updated_fields)
    except Author.DoesNotExist:
        pass  # User profili hali yaratilmagan bo‘lsa, xatolik chiqarmaydi
