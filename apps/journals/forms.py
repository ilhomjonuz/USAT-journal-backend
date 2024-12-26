from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import Journal, JournalVolume, JournalIssue


class JournalForm(forms.ModelForm):
    name_uz = forms.CharField(label='Journal Name (Uzbek)', required=True)
    name_ru = forms.CharField(label='Journal Name (Russian)', required=True)
    name_en = forms.CharField(label='Journal Name (English)', required=True)

    class Meta:
        model = Journal
        fields = ['name_en', 'name_ru', 'name_uz', 'description_en', 'description_ru', 'description_uz']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        # Add any custom validation if needed
        return cleaned_data


class JournalVolumeForm(forms.ModelForm):
    class Meta:
        model = JournalVolume
        fields = ['journal', 'volume_number', 'year']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save'))


class JournalIssueForm(forms.ModelForm):
    class Meta:
        model = JournalIssue
        fields = ['volume', 'issue_number', 'image', 'journal_file', 'start_page', 'end_page', 'publication_date', 'is_published']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save'))
