from django import forms
from django.contrib.auth.forms import (
    ReadOnlyPasswordHashField, AuthenticationForm)
from django.contrib.auth import password_validation

from things.models import User


class UserCreateForm(forms.ModelForm):
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput
    )
    password_conf = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(UserCreateForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['autofocus'] = 'on'

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')
        labels = {
            'email': 'Email address',
            'first_name': 'First name',
            'last_name': 'Last name',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('Email address is missing')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('User with this email already exists')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            try:
                password_validation.validate_password(password)
            except forms.ValidationError as validation_messages:
                self.add_error('password', validation_messages)
        return password

    def clean_password_conf(self):
        password = self.cleaned_data.get('password')
        password_conf = self.cleaned_data.get('password_conf')
        print(password, password_conf)
        if password and password_conf and password != password_conf:
            raise forms.ValidationError('Passwords don\'t match')
        return password_conf

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserAuthForm(AuthenticationForm):
    pass


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()
    password_new = forms.CharField(label='Password', widget=forms.PasswordInput, required=False)
    password_conf = forms.CharField(label='Password confirmation',
                                    widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ('email', 'password',
                  'first_name', 'last_name',
                  'is_superuser', 'is_admin')

    def clean_password(self):
        return self.initial.get("password")

    def clean_password_conf(self):
        password_new = self.cleaned_data.get("password_new")
        password_conf = self.cleaned_data.get("password_conf")
        if not password_new and not password_conf:
            return None
        if password_new and password_conf and password_new != password_conf:
            raise forms.ValidationError('Passwords don\'t match')
        return password_conf

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data['password_conf']:
            user.set_password(self.cleaned_data["password_new"])
            if commit:
                user.save()
        return user
