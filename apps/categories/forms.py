from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Category

class CategoryForm(forms.ModelForm):
    name_uz = forms.CharField(label=_('Category Name (Uzbek)'), required=True)
    name_ru = forms.CharField(label=_('Category Name (Russian)'), required=True)
    name_en = forms.CharField(label=_('Category Name (English)'), required=True)

    class Meta:
        model = Category
        fields = ['name_en', 'name_ru', 'name_uz', 'description_en', 'description_ru', 'description_uz', 'code']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            if field.startswith('description'):
                self.fields[field].widget = forms.Textarea(attrs={'class': 'form-control', 'rows': 3})


    def clean(self):
        cleaned_data = super().clean()
        # Add any custom validation if needed
        return cleaned_data
