from django.shortcuts import *
from .forms import StudentLoginForm
from .models import Student,TestInfo,CheatingReport,Question,Option,TestResult
import face_recognition
import cv2
import json
import numpy as np
import os
import random
import datetime
from django.views.generic import View,TemplateView
from django.http import HttpResponseRedirect, JsonResponse, Http404, HttpResponse
from django.core.exceptions import ValidationError

path = "/Users/infinity/Desktop/important/questionnaire/project/"
image_path = path + "media/students/"
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

class StudentLoginView(View):
    def get(self,request):
        form = StudentLoginForm()
        return render(request,'reg1.html',{"form":form})
    
    def post(self,request):
        bound_form = StudentLoginForm(request.POST)
        # print(bound_form)
        if bound_form.is_valid() :
            user = Student.objects.get(id = bound_form.cleaned_data['id'])
            if user.photo != "":
                if not facedect(user.photo.url):
                    raise ValidationError("Are you sure you are {}'s user?".format(user.id))
            else:
                user.photo = create_photo(user.id)
                user.save()
            return redirect('reg3',bound_form.cleaned_data['id'])
        return render(request,'reg1.html',{"form":bound_form})      


class AlreadyDoneView(TemplateView):
    template_name = "Done.html"

class NotYet(TemplateView):
    template_name = "not_available.html"


class TestInfoView(TemplateView):
    template_name = "reg3.html"
  

class TestView(TemplateView):
    template_name = "new_student_section.html"
    def get(self,request,user_id):
        test = get_object_or_404(TestInfo, id=65)
        student= get_object_or_404(Student, id=user_id)
        if TestResult.objects.filter(test=test,student=student).count() != 0:
            return redirect('wasDone')
        if not  test.is_active == TestInfo.TestState.ongoing:
            return redirect("NotYet")
        print(test.is_active)
        # if (datetime.datetime(test.end_time) - datatime.date.today).total_seconds()> test.duration*60:
        #     duration = test.duration * 60
        # elif (datetime.datetime(test.end_time) - datatime.date.today).total_seconds() < test.duration*60:
        #     duration = (datetime.datetime(test.end_time) - datatime.date.today).total_seconds()
        # else:
        #     duration = 0
        return render(request,"new_student_section.html", {'questions': test.questions.all(),'duration':test.duration,'user_id' :user_id })

def result(request,user_id):
    point = 0
    test = get_object_or_404(TestInfo, id=65)
    student= get_object_or_404(Student, id=user_id)
    if request.is_ajax() and request.method == 'POST':
        json_data = json.loads(request.body.decode('utf-8'))
        print(json_data)
        for data in json_data:
            question = Question.objects.get(id = data['id'])
            print(question)
            answers = Option.objects.filter(question = question)
            if question.is_multiple_choice and len(data['options']) > 1:
                for option in data['options']:
                    print(option)
                    print(answers)
                    if option in answers:
                        point += 1
            elif (not question.is_multiple_choice )and len(data['options']) == 1:
                if str(data['options'][0]) == str(answers[0].id):
                        point += 1

        print(point)
        result = TestResult(student = student,test=test,grade=point,submitted_date = datatime.date.today )
        print(result)
        result.save()
    return render(request, 'result.html')

def checkStudent(request,user_id):
    user = Student.objects.get(id = user_id)
    if not facedect(user.photo.url):
        report = CheatingReport()
        report.student = user
        report.test = TestInfo.objects.get(id=65)
        report.cheating_date = datatime.date.today
        report.reason = "Not the same person"
        report.save()
    elif  facedect(user.photo.url):
        return JsonResponse({'response': 'Student was successfully identificated'}, status=200)

    return JsonResponse({'error': 'ajax request is required'}, status=400)



def cheatingReport(request,user_id):
    if request.is_ajax() and request.method == 'POST':
        user = Student.objects.get(id = user_id)
        report = CheatingReport()
        report.student = user
        report.test = TestInfo.objects.get(id=65)
        report.cheating_date = datatime.date.today
        report.reason = json.loads(request.body.decode('utf-8'))
        report.save()
        return JsonResponse({'response': 'Student was successfully identificated'}, status=200)

