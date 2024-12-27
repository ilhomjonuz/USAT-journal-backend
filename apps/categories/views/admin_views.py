from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _

from apps.categories.models import Category
from apps.categories.forms import CategoryForm

class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'category-admin/category_list.html'
    context_object_name = 'categories'
    paginate_by = 10

    def get_queryset(self):
        return Category.objects.all().order_by('name')

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category-admin/category_form.html'
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Category created successfully.'))
        return response

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category-admin/category_form.html'
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Category updated successfully.'))
        return response

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'category-admin/category_confirm_delete.html'
    success_url = reverse_lazy('category_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()

        # Get related objects (adjust as needed based on your model relationships)
        articles = category.articles.all()

        related_objects = [
            {
                'name': _('Articles'),
                'count': articles.count(),
                'items': articles.values('title', 'status')[:5]
            },
        ]

        context['related_objects'] = related_objects
        context['has_related_objects'] = any(obj['count'] > 0 for obj in related_objects)
        return context

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, _("This category cannot be deleted because it is referenced by other objects."))
            return redirect('category_list')
