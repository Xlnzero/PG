from django import forms

class ContactForm(forms.Form):
    full_name = forms.CharField(label="ФИО", max_length=100, required=True)
    phone = forms.CharField(label="Номер телефона", max_length=20, required=True)
