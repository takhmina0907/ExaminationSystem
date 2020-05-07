import datetime

from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import (
    ReadOnlyPasswordHashField, AuthenticationForm)

from things.models import (
    User, TestInfo, Student, Speciality
)


class UserCreateForm(forms.ModelForm):
    fullname = forms.CharField(widget=forms.TextInput)
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(UserCreateForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter your e-mail'
        self.fields['fullname'].widget.attrs['autofocus'] = 'on'
        self.fields['fullname'].widget.attrs['placeholder'] = 'Fullname'
        self.fields['fullname'].widget.attrs['class'] = 'form-control'
        self.fields['place_of_work'].widget.attrs['placeholder'] = 'Where do you work?'
        self.fields['place_of_work'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['placeholder'] = 'Password'
        self.fields['password'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = User
        fields = ('email', 'place_of_work',)
        labels = {
            'email': 'Email address',
            'place_of_work': 'Where do you work?',
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

    def clean_fullname(self):
        fullname = self.cleaned_data.get('fullname')
        if fullname:
            if fullname.find(' ') == -1:
                self.add_error('fullname', 'Provide fullname(First name and Last name)')
        return fullname

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        fullname = self.cleaned_data['fullname'].split(' ', maxsplit=1)
        user.first_name = fullname[0]
        user.last_name = fullname[1]
        if commit:
            user.save()
        return user


class UserAuthForm(AuthenticationForm):
    username = forms.EmailField(
        label='',
        widget=forms.TextInput(
            attrs={'autofocus': True,
                   'placeholder': 'Enter your email'
                   }
        )
    )
    password = forms.CharField(
        label="",
        strip=False,
        widget=forms.PasswordInput(
            attrs={'placeholder': 'Password'}
        ),
    )

    def __init__(self, *args, **kwargs):
        super(UserAuthForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['class'] = 'form-control'

    def confirm_login_allowed(self, user):
        if not user.is_email_confirmed:
            raise forms.ValidationError(
                'Please confirm your email. Check your email for the confirmation link'
            )


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


class TestCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TestCreateForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['placeholder'] = 'Enter test name'
        self.fields['title'].widget.attrs['autofocus'] = 'on'
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['placeholder'] = 'Enter test description'
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['duration'].widget.attrs['placeholder'] = 'Enter test duration(min)'
        self.fields['duration'].widget.attrs['class'] = 'form-control'
        self.fields['start_date'].widget.attrs['placeholder'] = 'Choose the date'
        self.fields['start_date'].widget.attrs['class'] = 'form-control'
        self.fields['start_time'].widget.attrs['placeholder'] = 'Choose the time'
        self.fields['start_time'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = TestInfo
        fields = ('title', 'description', 'duration', 'start_date', 'start_time')

    description = forms.CharField(
        widget=forms.TextInput()
    )

    start_date = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date'}
        ))
    start_time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={'type': 'time'}
        ))

    def save(self, commit=True):
        test = super().save(commit=False)
        test.deadline = datetime.datetime.combine(self.cleaned_data['start_date'],
                                                  self.cleaned_data['start_time'])

        temp_date = datetime.datetime(1, 1, 1, self.cleaned_data['start_time'].hour,
                                      self.cleaned_data['start_time'].minute, self.cleaned_data['start_time'].second)

        temp_date = temp_date + datetime.timedelta(minutes=self.cleaned_data['duration'])
        test.end_time = temp_date.time()

        if commit:
            test.save()
        return test


class StudentTestAddForm(forms.Form):
    specialities = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                                  queryset=Speciality.objects.all())


class StudentCreateForm(forms.ModelForm):
    speciality = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(StudentCreateForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter student name'
        self.fields['first_name'].widget.attrs['autofocus'] = 'on'
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter student surname'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['id'].widget.attrs['placeholder'] = 'Enter student ID'
        self.fields['id'].widget.attrs['class'] = 'form-control'
        self.fields['speciality'].widget.attrs['placeholder'] = 'Enter or choose group'
        self.fields['speciality'].widget.attrs['class'] = 'form-control'
        self.fields['speciality'].widget.attrs['autocomplete'] = 'off'
        self.fields['speciality'].widget.attrs['list'] = 'specialities'

    class Meta:
        model = Student
        fields = ('first_name', 'last_name', 'id')

    def clean_speciality(self):
        speciality = self.cleaned_data['speciality']
        return speciality.strip().upper()

    # noinspection DuplicatedCode
    def save(self, commit=True):
        student = super().save(commit=False)
        student.speciality = Speciality.objects.get_or_create(
            title=self.cleaned_data['speciality'])[0]
        student.email = str(self.cleaned_data['id'])+'@stu.sdu.edu.kz'
        if commit:
            student.save()
        return student


class StudentEditForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(StudentEditForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter student name'
        self.fields['first_name'].widget.attrs['autofocus'] = 'on'
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter student surname'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['id'].widget.attrs['placeholder'] = 'Enter student ID'
        self.fields['id'].widget.attrs['class'] = 'form-control'
        self.fields['speciality'].widget.attrs['placeholder'] = 'Enter or choose group'
        self.fields['speciality'].widget.attrs['class'] = 'form-control'
        self.fields['speciality'].widget.attrs['autocomplete'] = 'off'
        self.fields['speciality'].widget.attrs['list'] = 'specialities'
        self.initial['speciality'] = self.instance.speciality

    class Meta:
        model = Student
        fields = ('first_name', 'last_name', 'id')

    speciality = forms.CharField()

    def clean_speciality(self):
        speciality = self.cleaned_data['speciality']
        return speciality.strip().upper()

    # noinspection DuplicatedCode
    def save(self, commit=True):
        student = super().save(commit=False)
        student.speciality = Speciality.objects.get_or_create(
            title=self.cleaned_data['speciality'])[0]
        student.email = str(self.cleaned_data['id'])+'@stu.sdu.edu.kz'
        if commit:
            student.save()
        return student
