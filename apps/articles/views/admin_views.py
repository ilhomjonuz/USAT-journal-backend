from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
import os

from apps.articles.forms import ArticleForm
from apps.articles.models import Article
from apps.categories.models import Category
from apps.journals.models import JournalIssue


class ArticleListView(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'article-admin/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()

        # Search
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(keywords__icontains=search_query) |
                Q(annotation__icontains=search_query)
            )

        # Status filter
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Category filter
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)

        # Journal Issue filter
        journal_issue = self.request.GET.get('journal_issue')
        if journal_issue:
            queryset = queryset.filter(journal_issue_id=journal_issue)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['article_status_choices'] = Article.STATUS_CHOICES
        context['journal_issues'] = JournalIssue.objects.all()
        return context


class ArticleCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'article-admin/article_form.html'
    success_url = reverse_lazy('article_list')
    success_message = _("Article was created successfully")


class ArticleUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'article-admin/article_form.html'
    success_url = reverse_lazy('article_list')
    success_message = _("Article was updated successfully")


class ArticleDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Article
    template_name = 'article-admin/article_confirm_delete.html'
    success_url = reverse_lazy('article_list')
    success_message = _("Article was deleted successfully")


class ArticleDetailView(LoginRequiredMixin, DetailView):
    model = Article
    template_name = 'article-admin/article_detail.html'

    def post(self, request, *args, **kwargs):
        article = self.get_object()
        action = request.POST.get('action')
        if action == 'set_under_review':
            article.set_under_review()
        elif action == 'accept':
            article.accept()
        elif action == 'reject':
            article.reject()
        elif action == 'publish':
            article.publish()
        messages.success(request, _("Article status changed to %(status)s") % {'status': article.get_status_display()})
        return redirect('article_detail', pk=article.pk)


def download_file(request, pk, file_type):
    # Get article
    article = get_object_or_404(Article, pk=pk)

    # Select file
    if file_type == 'original':
        file = article.original_file
    elif file_type == 'revised':
        file = article.revised_file
    else:
        messages.error(request, _("Invalid file type"), extra_tags='danger')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    # Check if file exists
    if not os.path.exists(file.path):
        messages.error(request, _("File not found"), extra_tags='danger')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    # Increment download count
    article.increment_download_count()

    # Send file as response
    response = FileResponse(open(file.path, 'rb'), as_attachment=True, filename=os.path.basename(file.path))
    return response


@login_required
@require_POST
def article_action(request):
    """Handle article status changes via AJAX"""
    article_id = request.POST.get('article_id')
    action = request.POST.get('action')

    if not article_id or not action:
        return JsonResponse({
            'status': 'error',
            'message': _('Missing required parameters')
        })

    article = get_object_or_404(Article, id=article_id)

    try:
        if action == 'set_under_review':
            article.set_under_review()
        elif action == 'accept':
            article.accept()
        elif action == 'reject':
            article.reject()
        elif action == 'publish':
            article.publish()
        else:
            return JsonResponse({
                'status': 'error',
                'message': _('Invalid action')
            })

        return JsonResponse({
            'status': 'success',
            'message': _('Article status changed to %(status)s') % {'status': article.get_status_display()}
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })
