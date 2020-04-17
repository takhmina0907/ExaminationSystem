from django import forms
from django.forms import ModelForm
from .models import Test

class LoginForm(forms.Form):
   id = forms.CharField(max_length = 100,)

class TestForm (ModelForm):
    class Meta:
        model = Test
        fields = ('number','sections','question', 'A', 'B', 'C','answer','data')
  
    
	