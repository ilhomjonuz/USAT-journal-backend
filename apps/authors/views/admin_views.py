from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from apps.authors.forms import AuthorForm
from apps.authors.models import Author

class AuthorListView(LoginRequiredMixin, ListView):
    model = Author
    template_name = 'author-admin/author_list.html'
    context_object_name = 'authors'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                models.Q(first_name__icontains=search_query) |
                models.Q(last_name__icontains=search_query) |
                models.Q(email__icontains=search_query)
            )
        return queryset.order_by('-created_at')

class AuthorCreateView(LoginRequiredMixin, CreateView):
    model = Author
    form_class = AuthorForm
    template_name = 'author-admin/author_form.html'
    success_url = reverse_lazy('author_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Author created successfully.'))
        return response

class AuthorUpdateView(LoginRequiredMixin, UpdateView):
    model = Author
    form_class = AuthorForm
    template_name = 'author-admin/author_form.html'
    success_url = reverse_lazy('author_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_delete_button'] = True  # Add this for the delete button
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Author updated successfully.'))
        return response

class AuthorDeleteView(LoginRequiredMixin, DeleteView):
    model = Author
    template_name = 'author-admin/author_confirm_delete.html'
    success_url = reverse_lazy('author_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('Author deleted successfully.'))
        return super().delete(request, *args, **kwargs)
