from django import forms
from .models import Shelf



class ShelfForm(forms.ModelForm):

    class Meta:
        
        model = Shelf
        fields = ['shelf_name']

    def clean_shelf_name(self):
        data = self.cleaned_data.get('shelf_name')
        
        if data == 'Hello':
            raise forms.ValidationError('Enter another name for the shelf')
        return data

class Update(forms.ModelForm):
    
    class Meta:

        model = Shelf
        fields = ['shelf_name']