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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
import things.views as views
from things.admin_views.views import (
    RegistrationView, LoginView, LogoutView,
    AdminTestListView, AdminTestCreateView,
    AdminTestDetailView, StudentResultDetailView,
    PreActivationView, ActivationView,
    StudentListView, StudentDetailView,
    StudentCreateView, StudentCreateSuccess,
    StudentDeleteView, TestDeleteView,
    StudentEditView, TestEditView,
    TestStudentAddView,
    copy_test, admin_question_delete,
    student_csv_import, admin_question_update,
    admin_test, admin_question_add, admin_option_add,
    students_results, check_speciality
)

urlpatterns = [
    path('superuser/', admin.site.urls),
    path('Test/<id>/result/',views.result, name='res'),
    path('Test/<id>',views.Test_view,name='test'),
    path('',views.reg1,name="reg1"),
    path('TestInfo/<id>',views.reg3,name='reg3'),
    path('notAvailable/<id>',views.no,name="notAvailable"),
    path('Cannot/<id>',views.cannot,name="Cannot"),
#----------------------------
    path('admin/register/', RegistrationView.as_view(), name='admin-registration'),
    path('admin/login/', LoginView.as_view(), name='admin-login'),
    path('admin/logout/', LogoutView.as_view(), name='admin-logout'),
    path('admin/pre-activate/', PreActivationView.as_view(), name='admin-pre-activation'),
    path('admin/activate/<uidb64>/<token>/', ActivationView.as_view(), name='admin-activation'),
    path('admin/<int:id>/tests/', AdminTestListView.as_view(), name='admin-tests'),
    path('admin/<int:id>/tests/create/', AdminTestCreateView.as_view(), name='admin-create-test'),
    path('admin/<int:user_id>/tests/<int:test_id>/', admin_test, name='admin-test'),
    path('admin/<int:user_id>/tests/<int:test_id>/groups/', TestStudentAddView.as_view(),
         name='admin-test-add-students'),
    path('admin/<int:user_id>/tests/<int:test_id>/edit/', TestEditView.as_view(), name='admin-edit-test'),
    path('admin/<int:user_id>/tests/<int:test_id>/delete/', TestDeleteView.as_view(), name='admin-delete-test'),
    path('admin/<int:user_id>/tests/<int:test_id>/copy/', copy_test, name='admin-copy-test'),
    path('admin/<int:user_id>/tests/<int:test_id>/details/', AdminTestDetailView.as_view(),
         name='admin-test-details'),
    path('admin/<int:user_id>/tests/<int:test_id>/result/<int:result_id>/', StudentResultDetailView.as_view(),
         name='admin-student-result'),
    path('admin/students/', StudentListView.as_view(), name='admin-students'),
    path('admin/students/<int:student_id>/', StudentDetailView.as_view(), name='admin-student-details'),
    path('admin/students/create/', StudentCreateView.as_view(), name='admin-create-student'),
    path('admin/students/create/csv/', student_csv_import, name='admin-create-student-csv'),
    path('admin/students/create/success/', StudentCreateSuccess.as_view(), name='admin-create-student-success'),
    path('admin/students/<int:student_id>/delete/', StudentDeleteView.as_view(), name='admin-delete-student'),
    path('admin/students/<int:student_id>/edit/', StudentEditView.as_view(), name='admin-edit-student'),

    # ajax
    path('admin/tests/<int:test_id>/questions/create', admin_question_add, name='admin-question-add'),
    path('questions/<int:question_id>/delete', admin_question_delete, name='admin-delete-question'),
    path('admin/tests/<int:test_id>/questions/<int:question_id>/update', admin_question_update,
         name='admin-question-update'),
    path('admin/tests/<int:test_id>/questions/<int:question_id>/options/create', admin_option_add,
         name='admin-option-add'),
    path('admin/tests/<int:test_id>/<str:sort_by>', students_results, name='admin-details-students'),
    path('admin/speciality', check_speciality, name='admin-check-speciality'),
    # ajax
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
