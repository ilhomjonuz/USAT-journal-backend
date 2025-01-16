from django import forms
from .models import Author

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['first_name', 'last_name', 'country', 'city', 'workplace', 'level', 'email', 'phone',
                  'telegram_contact', 'whatsapp_contact', 'academic_degree', 'academic_title', 'orcid']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'workplace': forms.TextInput(attrs={'class': 'form-control'}),
            'level': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'telegram_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'academic_degree': forms.Select(attrs={'class': 'form-select js-select2'}),
            'academic_title': forms.Select(attrs={'class': 'form-select js-select2'}),
            'orcid': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'placeholder': self.fields[field].label})

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            phone = ''.join(filter(str.isdigit, phone))
        return phone

    def clean_orcid(self):
        orcid = self.cleaned_data.get('orcid')
        return orcid
