from django.contrib import admin
from .models import User_table
from .models import Test,Country
from django.contrib.auth.admin import UserAdmin
class TestAdmin(admin.ModelAdmin):
	
	list_display = ['number','sections','question', 'A', 'B', 'C','D','E','answer','data',]
	list_filter=('sections','data')
	search_fields=('number','data','question')
admin.site.register(Test, TestAdmin)

class CountryAdmin(admin.ModelAdmin):
	list_display = ['country_name']

admin.site.register(Country, CountryAdmin)		

class UserAdmin(admin.ModelAdmin):
	
    list_display = ['id','country','university', 'speciality','score','date',]
    list_filter=('country','university', 'speciality','score','date')
    search_fields=('id',)
admin.site.register(User_table, UserAdmin)
