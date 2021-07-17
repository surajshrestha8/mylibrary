from django import forms
from django.db.models.base import Model
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from .models import Student
from django.contrib.auth.models import User
from crispy_forms.layout import Fieldset, Layout,ButtonHolder,Submit,Field
from crispy_forms.helper import FormHelper
from django.contrib.auth import authenticate

class StudentCreateForm(UserCreationForm):
    username = forms.CharField(required=True,widget=forms.TextInput(attrs={"placeholder":"Enter your username","id":"username"}),error_messages={"required":"Please enter a valid username"})
    email = forms.EmailField(required=True,widget=forms.EmailInput(attrs={"placeholder":"Enter your email address","id":"email"}))
    first_name = forms.CharField(max_length=20,widget=forms.TextInput(attrs={"placeholder":"Enter your first name","id":"Fname"}))
    last_name = forms.CharField(max_length=20,widget=forms.TextInput(attrs={"placeholder":"Enter your last name","id":"Lname"}))
  
    class Meta:
        
        model = User
        fields = ['username','email','first_name','last_name','password1','password2']

    
    def __init__(self, *args, **kwargs):
            super(StudentCreateForm, self).__init__(*args, **kwargs)

            self.helper = FormHelper()
            self.helper.layout = Layout(
                Field('username',css_id ="username"),
                Field('email',css_id="email"),
                Field('first_name',css_id="Fname"),
                Field('last_name',css_id="Lname"),
                Field('password1',css_id="user_pass"),
                Field('password2',css_id="confirm_pass"),
            )
           
                                   
            for fieldname in ['username', 'password1', 'password2']:
                self.fields[fieldname].help_text = None

    
  
    
    def save(self,commit=True):
        user = super().save(commit=False)
        
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_namme = self.cleaned_data['last_name']

        if commit:
            user.save()
        return user
    
    # def clean_username(self):
    #     username = self.cleaned_data.get('username')
    #     if username == 'surajshrestha8888':
    #         raise forms.ValidationError("Please enter another username")
            
    #     return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        try:
            match = User.objects.get(email=email)
        except User.DoesNotExist:
          return email  

        raise forms.ValidationError('Email already in use')

   
class StudentForm(ModelForm):

    class Meta:
        model = Student
        fields =['gender','faculty']


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=255, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user or not user.is_active:
            raise forms.ValidationError('Sorry, that login was invalid. Please try again.')
        return self.cleaned_data

    def login(self, request):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        return user