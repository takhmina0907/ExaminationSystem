from django import forms
from django.forms import ModelForm
from .models import Test,User_table

class SignUpForm(ModelForm):
      class Meta:
          model = User_table
          fields = ('id','country', 'university', 'speciality')
class IdForm(forms.Form):
  id=forms.IntegerField()
    

class TestForm (ModelForm):
    class Meta:
        model = Test
        fields = ('number','sections','question', 'A', 'B', 'C','answer','data')
  
    
	