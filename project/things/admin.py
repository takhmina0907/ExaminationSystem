from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Test,User
from .models import TestInfo, Question, Option, Student, TestResult, Answer, Speciality,StudentImage
from things.admin_forms.forms import UserCreateForm, UserChangeForm


class TestAdmin(admin.ModelAdmin):
    list_display = ['number', 'sections', 'question', 'A', 'B', 'C', 'D', 'E', 'answer', 'data', ]
    list_filter = ('sections', 'data')
    search_fields = ('number', 'data', 'question')
admin.site.register(Test, TestAdmin)

class NewUserAdmin(DjangoUserAdmin):
    form = UserChangeForm
    add_form = UserCreateForm
    search_fields = ('id', 'email', 'first_name', 'last_name')

    list_display = ('id', 'email', 'first_name', 'last_name')
    list_filter = ('is_admin', 'is_email_confirmed')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password', 'is_email_confirmed')}),
        ('Change password', {'fields': ('password_new', 'password_conf')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_superuser', 'is_admin')}),
    )

    add_fieldsets = (
        (None, {
            'fields': ('email', 'password_new', 'password_conf')
        }),
    )
admin.site.register(User, NewUserAdmin)


@admin.register(TestInfo, Question, Option, Student,StudentImage, TestResult, Answer, Speciality)
class BasicAdmin(admin.ModelAdmin):
    pass
