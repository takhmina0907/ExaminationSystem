from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User_table, User
from .models import Test, Country
from .models import TestInfo, Question, Option, Student, TestResult, Answer
from things.admin_forms.forms import UserCreateForm, UserChangeForm


class TestAdmin(admin.ModelAdmin):
    list_display = ['number', 'sections', 'question', 'A', 'B', 'C', 'D', 'E', 'answer', 'data', ]
    list_filter = ('sections', 'data')
    search_fields = ('number', 'data', 'question')
admin.site.register(Test, TestAdmin)


class CountryAdmin(admin.ModelAdmin):
    list_display = ['country_name']
admin.site.register(Country, CountryAdmin)


class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'country', 'university', 'speciality', 'score', 'date', ]
    list_filter = ('country', 'university', 'speciality', 'score', 'date')
    search_fields = ('id',)
admin.site.register(User_table, UserAdmin)


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


@admin.register(TestInfo, Question, Option, Student, TestResult, Answer)
class BasicAdmin(admin.ModelAdmin):
    pass
