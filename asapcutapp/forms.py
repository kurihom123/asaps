from django import forms
from .models import Contribution
from .models import ContributionUpload

class ContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ['association', 'amount_paid', 'payment_date', 'year']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
        }

        def __init__(self, *args, **kwargs):
            self.user = kwargs.pop('user', None)  # 👈 this line makes user available
            super().__init__(*args, **kwargs)

class ContributionFormYear(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ['association', 'amount_paid', 'payment_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'



class ExcelUploadForm(forms.ModelForm):
    class Meta:
        model = ContributionUpload
        fields = ['excel_file', 'year']
        widgets = {
            'year': forms.TextInput(attrs={'class': 'form-control'}),
            'excel_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx,.xls'})
        }