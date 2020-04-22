import datetime
import enum

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from .directionOfFile import images_upload,student_photo_upload


class Test(models.Model):
    number=models.IntegerField();
    SECTION_TYPE = (
        (1, 'English'),
        (2, 'Russion'),
    );
    sections = models.PositiveSmallIntegerField(choices=SECTION_TYPE);
    question=models.TextField(default='')
    img=models.ImageField(upload_to=images_upload,default='',blank=True)
    second_part=models.TextField(default='',blank=True)
    A=models.CharField(max_length=1024)
    B=models.CharField(max_length=1024)
    C=models.CharField(max_length=1024)
    D=models.CharField(max_length=1024 ,blank=True,default="")
    E=models.CharField(max_length=1024 ,blank=True,default="")
    answer=models.CharField(max_length=256)
    data=models.DateField(default="2018-01-01")
    def __str__(self):
        return self.answer

class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_admin', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=False)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    place_of_work = models.CharField(max_length=256)
    is_email_confirmed = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'place_of_work']

    objects = UserManager()

    @property
    def is_staff(self):
        return self.is_admin


class Speciality(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class Student(models.Model):
    id = models.IntegerField(blank=True, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    speciality = models.ForeignKey(Speciality, on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True)
    photo = models.ImageField(upload_to=student_photo_upload,default='',blank=True)

    def __str__(self):
        return '{} - {} - {}'.format(self.id, self.first_name, self.speciality)


class TestInfo(models.Model):
    title = models.CharField(max_length=500, null=False, blank=False)
    description = models.TextField(blank=False, null=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tests')
    created_date = models.DateTimeField(auto_now_add=True, blank=True)
    deadline = models.DateTimeField(blank=False, null=False)
    start_date = models.DateField(blank=False, null=False)
    start_time = models.TimeField(blank=False, null=False)
    end_time = models.TimeField(blank=False, null=False)
    duration = models.PositiveSmallIntegerField()
    is_visible = models.BooleanField(default=True)
    link = models.TextField(blank=True)
    students = models.ManyToManyField(Student, related_name='tests', blank=True)

    class TestState(enum.Enum):
        not_started = 'Not Started'
        ongoing = 'Ongoing'
        finished = 'Finished'

    @property
    def is_active(self):
        now = datetime.datetime.now()
        start = datetime.datetime.combine(self.start_date,
                                          self.start_time)
        end = datetime.datetime.combine(self.start_date,
                                        self.end_time)
        if now < start:
            return self.TestState.not_started
        elif now > end:
            return self.TestState.finished
        else:
            return self.TestState.ongoing
        # return self.deadline > timezone.now()

    def __str__(self):
        return '{} - {}'.format(self.id, self.author.email)


class Question(models.Model):
    test = models.ForeignKey(TestInfo, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField(blank=False, null=False)
    is_multiple_choice = models.BooleanField(default=False)

    def __str__(self):
        return '{} - {}'.format(self.test.title, self.question)


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option = models.CharField(max_length=1024, null=False, blank=False)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return '{} - {}'.format(self.option, self.question.question)


class TestResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    test = models.ForeignKey(TestInfo, on_delete=models.CASCADE, related_name='results')
    grade = models.FloatField()
    submitted_date = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return '{} - {}'.format(self.test.title, self.student.id)


class Answer(models.Model):
    test = models.ForeignKey(TestResult, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Option, on_delete=models.CASCADE)

    def __str__(self):
        return '{} - {}'.format(self.question.question, self.answer.option)
