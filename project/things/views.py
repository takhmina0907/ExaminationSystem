from django.shortcuts import *
from .forms import StudentLoginForm
from .models import Student,TestInfo,CheatingReport,Question,Option,TestResult
from .mixin import TestLinkMixin
import face_recognition
import cv2
import json
import numpy as np
import os
import random
import datetime 
from django.views.generic import View,TemplateView
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http import HttpResponseRedirect, JsonResponse, Http404, HttpResponse
from django.core.exceptions import ValidationError
from least.settings import BASE_DIR

path = BASE_DIR
image_path = path + "/media/students/"
# Create your views here.
# для того что бы сравнить фото с видео 
def facedect(loc):
        cam = cv2.VideoCapture(0)   #включить камеру
        s, img = cam.read()
        if s: #проверка камеры
                BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                
                MEDIA_ROOT =os.path.join(BASE_DIR) #путь до фотки
                
                loc=(str(MEDIA_ROOT)+loc)
                face_1_image = face_recognition.load_image_file(loc)
                print(face_1_image)
                print(face_recognition.face_encodings(face_1_image))
                face_1_face_encoding = face_recognition.face_encodings(face_1_image)[0] #перевести фотку в массив

                face_locations = face_recognition.face_locations(img) #из видео получить лицо
                if face_locations: #если есть лицо
                    face_encodings = face_recognition.face_encodings(img, face_locations) #перевести лицо в массив
                    check=face_recognition.compare_faces(face_1_face_encoding, face_encodings) #проверка на совместимость
                    print(check)
                    if check[0]:
                            return True
                    else :
                            return False   

def create_photo(id):
    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(path + '/cascade/haarcascade_frontalface_alt2.xml')
    while 1:
        ret, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        print(faces)
        for (x,y,w,h) in faces:
            cv2.rectangle(img,(x+1000,y+1000),(x+w+1000,y+h+1000),(255,0,0),2)
            roi_gray = gray[y:y+h, x:x+w]
            if not os.path.isfile(image_path + str(id)):# надо сделать что то с тем если папка существует
                os.makedirs(image_path + str(id))
            image = image_path + str(id)+ "/image.png"
            image_item ="/students/" + str(id)+"/image.png"
            cv2.imwrite(image,roi_gray)
            return image_item 

class StudentLoginView(TestLinkMixin,View):
    login_url = "notAvailable/404"
    def get(self,request,uidb64):
        form = StudentLoginForm()
        return render(request,'reg1.html',{"form":form,"uidb64":uidb64})
    
    def post(self,request,uidb64):
        bound_form = StudentLoginForm(request.POST)
        test_id = force_text(urlsafe_base64_decode(uidb64))
        test = TestInfo.objects.get(id=test_id)
        if bound_form.is_valid() :
            user = Student.objects.get(id = bound_form.cleaned_data['id'])
            if user in test.students.all():
                if user.photo != "":
                    if not facedect(user.photo.url):
                        message = "Are you sure you are {}'s user?".format(user.id)
                        return render(request,'reg1.html',{"form":bound_form,"message":message,"uidb64":uidb64})  
                else:
                    user.photo = create_photo(user.id)
                    user.save()
                uidb64_student=urlsafe_base64_encode(force_bytes(bound_form.cleaned_data['id']))
                return redirect('reg3',uidb64,uidb64_student)
            return render(request,'reg1.html',{"form":bound_form,"message":"You are not alloweded to pass test","uidb64":uidb64})  
        return render(request,'reg1.html',{"form":bound_form,"uidb64":uidb64})  



class NotYet(TemplateView):
    template_name = "not_available.html"



class TestInfoView(TestLinkMixin,TemplateView):
    template_name = "reg3.html"
  

class TestView(TestLinkMixin,TemplateView):
    template_name = "new_student_section.html"
    def get(self,request,uidb64,uidb64_student):
        student_id = force_text(urlsafe_base64_decode(uidb64_student))
        test_id = force_text(urlsafe_base64_decode(uidb64))
        test = get_object_or_404(TestInfo, id=test_id)
        student= get_object_or_404(Student, id=student_id)
        testResult = TestResult.objects.get(test=test,student=student)
        if testResult.grade is not None:
            redirect("NotYet")
        # if (datetime.datetime(test.end_time) - datatime.date.today).total_seconds()> test.duration*60:
        #     duration = test.duration * 60
        # elif (datetime.datetime(test.end_time) - datatime.date.today).total_seconds() < test.duration*60:
        #     duration = (datetime.datetime(test.end_time) - datatime.date.today).total_seconds()
        # else:
        #     duration = 0
        return render(request,"new_student_section.html", {'questions': test.questions.all(),'duration':test.duration,'uidb64_student' :uidb64_student })

def result(request,uidb64_student,uidb64):
    point = 0
    test_id = force_text(urlsafe_base64_decode(uidb64))
    student_id = force_text(urlsafe_base64_decode(uidb64_student))
    test = get_object_or_404(TestInfo, id=test_id)
    student= get_object_or_404(Student, id=student_id)
    if request.is_ajax() and request.method == 'POST':
        json_data = json.loads(request.body.decode('utf-8'))
        print(json_data)
        for data in json_data:
            question = Question.objects.get(id = data['id'])
            print(question)
            answers = Option.objects.filter(question = question,is_correct=True)
            if question.is_multiple_choice and len(data['options']) > 1:
                for option in data['options']:
                    print(option)
                    print(answers)
                    if option in answers:
                        point += 1
            elif (not question.is_multiple_choice )and len(data['options']) == 1:
                print(str(data['options'][0]),str(answers[0].id))
                if str(data['options'][0]) == str(answers[0].id):
                        point += 1

        print(point)
        result = TestResult.objects.get(test=test,student=student)
        result.grade = point
        print(datetime.date.today())
        result.submitted_date = datetime.datetime.now()
        #  = TestResult(student = student,test=test,grade=point,submitted_date = datetime.date.today )
        print(1234)
        result.save()
    return render(request, 'result.html')

def checkStudent(request,uidb64_student,uidb64):
    student_id = force_text(urlsafe_base64_decode(uidb64_student))
    user = Student.objects.get(id = student_id)
    test_id = force_text(urlsafe_base64_decode(uidb64))
    if not facedect(user.photo.url):
        report = CheatingReport()
        report.student = user
        report.test = TestInfo.objects.get(id=test_id)
        report.cheating_date = datetime.date.today
        report.reason = "Not the same person"
        report.save()
    elif  facedect(user.photo.url):
        return JsonResponse({'response': 'Student was successfully identificated'}, status=200)

    return JsonResponse({'error': 'ajax request is required'}, status=400)



def cheatingReport(request,uidb64_student,uidb64):
    student_id = force_text(urlsafe_base64_decode(uidb64_student))
    test_id = force_text(urlsafe_base64_decode(uidb64))
    if request.is_ajax() and request.method == 'POST':
        user = Student.objects.get(id = student_id)
        report = CheatingReport()
        report.student = user
        report.test = TestInfo.objects.get(id=test_id)
        report.cheating_date = datetime.date.today
        report.reason = json.loads(request.body.decode('utf-8'))
        report.save()
        return JsonResponse({'response': 'Student was successfully identificated'}, status=200)

