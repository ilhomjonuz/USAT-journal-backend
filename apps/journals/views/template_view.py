from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.journals.forms import JournalForm, JournalVolumeForm, JournalIssueForm
from apps.journals.models import Journal, JournalVolume, JournalIssue


class JournalListView(LoginRequiredMixin, ListView):
    model = Journal
    template_name = 'journal_admin/journal_list.html'
    context_object_name = 'journals'

class JournalDetailView(LoginRequiredMixin, DetailView):
    model = Journal
    template_name = 'journal_admin/journal_detail.html'

class JournalCreateView(LoginRequiredMixin, CreateView):
    model = Journal
    form_class = JournalForm
    template_name = 'journal_admin/journal_form.html'
    success_url = reverse_lazy('journal_admin:journal_list')

class JournalUpdateView(LoginRequiredMixin, UpdateView):
    model = Journal
    form_class = JournalForm
    template_name = 'journal_admin/journal_form.html'
    success_url = reverse_lazy('journal_admin:journal_list')

class JournalDeleteView(LoginRequiredMixin, DeleteView):
    model = Journal
    template_name = 'journal_admin/journal_confirm_delete.html'
    success_url = reverse_lazy('journal_admin:journal_list')

# Similar views for JournalVolume
class JournalVolumeListView(LoginRequiredMixin, ListView):
    model = JournalVolume
    template_name = 'journal_admin/volume_list.html'
    context_object_name = 'volumes'

class JournalVolumeDetailView(LoginRequiredMixin, DetailView):
    model = JournalVolume
    template_name = 'journal_admin/volume_detail.html'

class JournalVolumeCreateView(LoginRequiredMixin, CreateView):
    model = JournalVolume
    form_class = JournalVolumeForm
    template_name = 'journal_admin/volume_form.html'
    success_url = reverse_lazy('journal_admin:volume_list')

class JournalVolumeUpdateView(LoginRequiredMixin, UpdateView):
    model = JournalVolume
    form_class = JournalVolumeForm
    template_name = 'journal_admin/volume_form.html'
    success_url = reverse_lazy('journal_admin:volume_list')

class JournalVolumeDeleteView(LoginRequiredMixin, DeleteView):
    model = JournalVolume
    template_name = 'journal_admin/volume_confirm_delete.html'
    success_url = reverse_lazy('journal_admin:volume_list')

# Similar views for JournalIssue
class JournalIssueListView(LoginRequiredMixin, ListView):
    model = JournalIssue
    template_name = 'journal_admin/issue_list.html'
    context_object_name = 'issues'

class JournalIssueDetailView(LoginRequiredMixin, DetailView):
    model = JournalIssue
    template_name = 'journal_admin/issue_detail.html'

class JournalIssueCreateView(LoginRequiredMixin, CreateView):
    model = JournalIssue
    form_class = JournalIssueForm
    template_name = 'journal_admin/issue_form.html'
    success_url = reverse_lazy('journal_admin:issue_list')

class JournalIssueUpdateView(LoginRequiredMixin, UpdateView):
    model = JournalIssue
    form_class = JournalIssueForm
    template_name = 'journal_admin/issue_form.html'
    success_url = reverse_lazy('journal_admin:issue_list')

class JournalIssueDeleteView(LoginRequiredMixin, DeleteView):
    model = JournalIssue
    template_name = 'journal_admin/issue_confirm_delete.html'
    success_url = reverse_lazy('journal_admin:issue_list')
