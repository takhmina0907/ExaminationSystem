"""new URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
import things.views as views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('Test/<id>/result/',views.result, name='res'),
    path('Test/<id>',views.Test_view,name='test'),
    path('registration1',views.reg1,name="reg1"),
    path('',views.index,name='home'),
    path('registration2/<id>',views.reg2,name='reg2'),
    #path('registration3/<id>',views.reg4,name='reg4'),
    path('registration4/<id>',views.reg3,name='reg3'),
    path('notAvailable/<id>',views.no,name="notAvailable"),
    path('Cannot/<id>',views.cannot,name="Cannot"),
    #path('check',views.otchet,name="ot"),
    #path('export/csv/', views.export_users_csv, name='export_users_csv'),

#     path('ForDiana',views.Diana,name='Diana'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)