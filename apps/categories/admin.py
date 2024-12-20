from django.contrib import admin

from apps.categories.models import Category


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')

admin.site.register(Category, CategoryAdmin)
