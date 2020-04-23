from django.shortcuts import *
from .forms import StudentLoginForm
from .models import Test,Student
import face_recognition
import cv2
import numpy as np
import os
import random
from datetime import date
from django.views.generic import View,TemplateView
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
            cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
            roi_gray = gray[y:y+h, x:x+w]
            if not os.path.isfile(image_path + str(id)):
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
        print(bound_form)
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


# 

def no(request,id):
    return render(request,'not_available.html',{'id':id})

def cannot(request,id):
    return render(request,'done.html',{'id':id})

class TestInfo(TemplateView):
    template_name = "reg3.html"

class Test(TemplateView):
    template_name = "new_student_section.html"

def Test_view(request,id):
    arr = ['0:10', '10:20', '20:30', '30:40', '40:51']
    random.shuffle(arr)
    ch = arr[0].split(':')
    arr.remove(arr[0])
    finance=Test.objects.filter(sections=1,data=date.today())[int(ch[0]):int(ch[1])]
    ch = arr[0].split(':')
    arr.remove(arr[0])
    market=Test.objects.filter(sections=1,data=date.today())[int(ch[0]):int(ch[1])]
    ch = arr[0].split(':')
    arr.remove(arr[0])
    sd=Test.objects.filter(sections=1,data=date.today())[int(ch[0]):int(ch[1])]
    ch = arr[0].split(':')
    arr.remove(arr[0])
    ede=Test.objects.filter(sections=1,data=date.today())[int(ch[0]):int(ch[1])]
    ch = arr[0].split(':')
    arr.remove(arr[0])
    ede2=Test.objects.filter(sections=1,data=date.today())[int(ch[0]):int(ch[1])]


    return render(request,'finance.html',{'finance':ede2,'markets':ede,'analyses':sd,'calc':market,'theory':finance,'id':id})



def result(request,id):
    a = request.GET['res']
    correct = 0
    d={}
    a = a.replace(",", "")
    i=0
    while i<len(a)-2:
        if (a[i+1].isdigit() and a[i].isdigit()):
            d[a[i]+a[i+1]]=a[i+2]
            i=i+3
        elif a[i].isdigit():
            d[a[i]]=a[i+1]
            i=i+2
    for key in d:
        value = d[key]
        ans=Test.objects.filter(number=int(key),sections=1,data=date.today())
        if(value is str(ans[0])):
            correct+=1
    # install = User_table.objects.get(id=id)
    # install.string=a
    # install.sections=1
    # install.score=correct
    # install.date=date.today()
    # install.save()
    return render(request, 'result.html')



