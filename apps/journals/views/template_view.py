from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _

from apps.journals.forms import JournalForm, JournalVolumeForm, JournalIssueForm
from apps.journals.models import Journal, JournalVolume, JournalIssue


class JournalListView(LoginRequiredMixin, ListView):
    model = Journal
    template_name = 'journal_admin/journal_list.html'
    context_object_name = 'journals'


class JournalCreateView(LoginRequiredMixin, CreateView):
    model = Journal
    form_class = JournalForm
    template_name = 'journal_admin/journal_form.html'
    success_url = reverse_lazy('journal_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Journal created successfully.'))
        return response


class JournalUpdateView(LoginRequiredMixin, UpdateView):
    model = Journal
    form_class = JournalForm
    template_name = 'journal_admin/journal_form.html'
    success_url = reverse_lazy('journal_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Journal updated successfully.'))
        return response

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        if pk:
            return Journal.objects.get(pk=pk)
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object:
            context['object'] = self.object
        return context


class JournalDeleteView(LoginRequiredMixin, DeleteView):
    model = Journal
    template_name = 'journal_admin/journal_confirm_delete.html'
    success_url = reverse_lazy('journal_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        journal = self.get_object()

        # Get related objects with more details
        volumes = JournalVolume.objects.filter(journal=journal)
        issues = JournalIssue.objects.filter(volume__journal=journal)

        related_objects = [
            {
                'name': 'Volumes',
                'count': volumes.count(),
                'items': volumes.values('volume_number', 'year')
            },
            {
                'name': 'Issues',
                'count': issues.count(),
                'items': issues.values('volume__volume_number', 'issue_number', 'publication_date')
            },
        ]

        context['related_objects'] = related_objects
        context['has_related_objects'] = any(obj['count'] > 0 for obj in related_objects)
        return context

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError as e:
            messages.error(request, _("This journal cannot be deleted because it is referenced by other objects. {}".format(e)))
            return redirect('journal_list')


# Similar views for JournalVolume
class JournalVolumeListView(LoginRequiredMixin, ListView):
    model = JournalVolume
    template_name = 'journal_admin/volume_list.html'
    context_object_name = 'volumes'
    paginate_by = 10

    def get_queryset(self):
        return JournalVolume.objects.select_related('journal').order_by('-year', '-volume_number')

class JournalVolumeCreateView(LoginRequiredMixin, CreateView):
    model = JournalVolume
    form_class = JournalVolumeForm
    template_name = 'journal_admin/volume_form.html'
    success_url = reverse_lazy('volume_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Journal Volume created successfully.'))
        return response

class JournalVolumeUpdateView(LoginRequiredMixin, UpdateView):
    model = JournalVolume
    form_class = JournalVolumeForm
    template_name = 'journal_admin/volume_form.html'
    success_url = reverse_lazy('volume_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Journal Volume updated successfully.'))
        return response

class JournalVolumeDeleteView(LoginRequiredMixin, DeleteView):
    model = JournalVolume
    template_name = 'journal_admin/volume_confirm_delete.html'
    success_url = reverse_lazy('volume_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        volume = self.get_object()

        issues = JournalIssue.objects.filter(volume=volume)

        related_objects = [
            {
                'name': _('Issues'),
                'count': issues.count(),
                'items': issues.values('issue_number', 'publication_date')
            },
        ]

        context['related_objects'] = related_objects
        context['has_related_objects'] = any(obj['count'] > 0 for obj in related_objects)
        return context

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, _("This volume cannot be deleted because it is referenced by other objects."))
            return redirect('volume_list')


# Similar views for JournalIssue
class JournalIssueListView(LoginRequiredMixin, ListView):
    model = JournalIssue
    template_name = 'journal_admin/issue_list.html'
    context_object_name = 'issues'
    paginate_by = 10

    def get_queryset(self):
        return JournalIssue.objects.select_related('volume__journal').order_by('-publication_date', '-issue_number')


class JournalIssueCreateView(LoginRequiredMixin, CreateView):
    model = JournalIssue
    form_class = JournalIssueForm
    template_name = 'journal_admin/issue_form.html'
    success_url = reverse_lazy('issue_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Journal Issue created successfully.'))
        return response


class JournalIssueUpdateView(LoginRequiredMixin, UpdateView):
    model = JournalIssue
    form_class = JournalIssueForm
    template_name = 'journal_admin/issue_form.html'
    success_url = reverse_lazy('issue_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Journal Issue updated successfully.'))
        return response


class JournalIssueDeleteView(LoginRequiredMixin, DeleteView):
    model = JournalIssue
    template_name = 'journal_admin/issue_confirm_delete.html'
    success_url = reverse_lazy('issue_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        issue = self.get_object()

        articles = issue.articles.all()

        related_objects = [
            {
                'name': _('Articles'),
                'count': articles.count(),
                'items': articles.values('title', 'status')
            },
        ]

        context['related_objects'] = related_objects
        context['has_related_objects'] = any(obj['count'] > 0 for obj in related_objects)
        return context

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, _("This issue cannot be deleted because it is referenced by other objects."))
            return redirect('issue_list')
