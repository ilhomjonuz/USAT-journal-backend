from django import forms
from .models import Article
from ..categories.models import Category


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['category', 'title', 'keywords', 'annotation', 'authors', 'original_file', 'revised_file', 'start_page', 'end_page']
        widgets = {
            'keywords': forms.TextInput(attrs={'placeholder': 'Enter keywords separated by commas'}),
            'annotation': forms.Textarea(attrs={'rows': 4}),
            'authors': forms.SelectMultiple(attrs={'class': 'select2'}),
        }

class ArticleFilterForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Search articles...'}))
    status = forms.ChoiceField(choices=[('', 'All')] + Article.STATUS_CHOICES, required=False)
    category = forms.ModelChoiceField(queryset=None, required=False, empty_label="All Categories")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
