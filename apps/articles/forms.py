from django import forms
from .models import Article
from ..categories.models import Category


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['category', 'title', 'annotation', 'keywords', 'references', 'authors', 'anti_plagiarism_certificate', 'original_file', 'revised_file', 'publication_certificate', 'start_page', 'end_page', 'journal_issue', 'status']
        widgets = {
            'annotation': forms.Textarea(attrs={'rows': 4}),
            'keywords': forms.TextInput(attrs={'placeholder': 'Enter keywords separated by commas'}),
            'authors': forms.SelectMultiple(attrs={'class': 'select2'}),
            'journal_issue': forms.Select(attrs={'class': 'select2'}),
            'status': forms.Select(attrs={'class': 'select2'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk is None:  # If creating a new article
            self.fields.pop('status')  # Remove the status field


class ArticleFilterForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Search articles...'}))
    status = forms.ChoiceField(choices=[('', 'All')] + Article.STATUS_CHOICES, required=False)
    category = forms.ModelChoiceField(queryset=None, required=False, empty_label="All Categories")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
