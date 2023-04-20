from django import forms

class myForm(forms.Form):
    name=forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'name', 'style': 'width: 200px;margin: 10px'}))
    category=forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 200px;margin: 10px'}))