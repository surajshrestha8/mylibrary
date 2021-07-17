from django import forms
from .models import Book, Register
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms import formset_factory

class Create(forms.ModelForm):
    

    class Meta:
        
        model = Book
        fields = ['title','isbn','author','publisher']

    def __init__(self, *args, **kwargs):
        super(Create, self).__init__(*args, **kwargs)
        ## add a "form-control" class to each form input
        ## for enabling bootstrap
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
            })

class UpdateBook(forms.ModelForm):

    class Meta:

        model = Book
        fields = ['title','isbn','author','publisher']

class RegisterBook(forms.ModelForm):

    class Meta:
        model = Register
        fields =['shelf','number_of_copies']

