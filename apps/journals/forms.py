from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import Journal, JournalVolume, JournalIssue

class JournalForm(forms.ModelForm):
    class Meta:
        model = Journal
        fields = ['name', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save'))

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
