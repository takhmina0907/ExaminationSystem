from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.encoding import force_bytes, force_text
from .models import TestInfo,Student,TestResult
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.shortcuts import *
from django.core.exceptions import ValidationError
class TestLinkMixin(UserPassesTestMixin):
    login_url = ""
    def test_func(self):
        test = None
        path=self.request.path.split("/")
        uidb64_test = path[2] 
        print(path)
        status = "" 
         #------------------------------------------------------------
        # If test exist 
        try:
            test_id = force_text(urlsafe_base64_decode(uidb64_test))
            print(test_id)
            test = TestInfo.objects.get(id=test_id)
            print(test)
            correct_test = True
            status = test.is_active
        except (TypeError, ValueError, OverflowError, TestInfo.DoesNotExist, ValidationError):
            correct_test = False
        #------------------------------------------------------------
        # Authenticate Student 
        isStudentLink= False
        if len(path)>4:
            isStudentLink = True
            try:
                uidb64_student = path[3] 
                student_id = force_text(urlsafe_base64_decode(uidb64_student))
                print(student_id)
                student = Student.objects.get(id=student_id)
                print(student)
                testResult = TestResult.objects.get(test=test,student=student)
                correct_student = True
            except (TypeError, ValueError, OverflowError, TestResult.DoesNotExist,Student.DoesNotExist, ValidationError):
                correct_student = False
         #------------------------------------------------------------
     
        if correct_test and status == TestInfo.TestState.ongoing:
            if isStudentLink and correct_student and testResult.grade is None:
                return True
            elif not isStudentLink :
                print(11111)
                return True
            # TODO change redirect url
            return False
        else:
            # TODO change redirect url
            return False
    def handle_no_permission(self):
        '''to:[login,Profile] will signup or create profiles'''
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect('NotYet')
