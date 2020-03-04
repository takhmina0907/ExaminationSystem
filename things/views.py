from django.shortcuts import *
from django.shortcuts import render
from .forms import SignUpForm,IdForm
from .models import Test,User_table
import csv
from django.http import JsonResponse
from django.http import HttpResponse

import random
from datetime import date
# Create your views here.
def index(request):
    return render(request,'index2.html')
        
def reg1(request):
    error=False
    if request.method == 'POST':
        form = IdForm(request.POST)
        if form.is_valid():
            id_field=form.cleaned_data['id']
            if User_table.objects.filter(id=id_field,checking=False).exists():
                return redirect('reg2',id_field)
            else:
                return render(request, 'reg1.html', {'form': form,'error':True})
    else:
        form = IdForm()
    return render(request, 'reg1.html', {'form': form,'error':error})

def reg2(request,id):
    error=False;
    print(id)
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        form.id=id
        if form.is_valid():
            print(form.id)
            university=form.cleaned_data['university']
            speciality=form.cleaned_data['speciality']
            
            to_update = User_table.objects.filter(id=id).update(university=university,speciality=speciality,checking=False)
            
            return render(request,'reg3.html',{'id':id})
    else:
        form = SignUpForm()
    return render(request, 'reg2.html', {'form': form,'id':id})

def no(request,id):
    return render(request,'not_available.html',{'id':id});

def cannot(request,id):
    return render(request,'done.html',{'id':id});

def reg3(request,id):
    #a=request.GET.get('root')
    return render(request,'reg3.html',{'id':id});

def Test_view(request,id):
    if User_table.objects.get(id=id).checking:
        return redirect("Cannot",user)

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
    correct = 0;
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
            correct+=1;
    install = User_table.objects.get(id=id)
    install.string=a
    install.sections=1
    install.score=correct;
    install.date=date.today()
    install.save()
    return render(request, 'result.html')


def otchet(request):
    d={}
    correct=0
    correct_d={}
    i=0
    installs=User2.objects.filter(date='2018-12-28');
    for install in installs:
        correct=0;
        print('end6')
        correct_d={}
        d={}
        a=install.string
        print('string')
        print(install.user)
        i=0
        if a is not None:
            a = a.replace(",", '')
            a = a.replace("'", '')
            a = a.replace(":", '')
            a = a.replace("}", '')
            a = a.replace("{", '')
            print(a)
            while i<len(a)-2:
                print(i)
                if (a[i+1].isdigit() and a[i].isdigit()):
                    d[a[i]+a[i+1]]=a[i+2]
                    i=i+3
                elif a[i].isdigit():
                    d[a[i]]=a[i+1]
                    i=i+2
                elif a[i] is " ":
                    i=i+1
            print(d)
            for key in d:

                value = d[key]
                print(key+value)
                ans=Test.objects.filter(number=int(key),sections=install.sections,data=install.date)
                if(value is str(ans[0])):
                    correct+=1;
                else:
                    correct_d[key]=value
            print('end')
        install.Notcorrect=correct_d;
        print('end2')
        install.string=d
        print('end3')
        install.score=correct
        print('end4')
        install.save();
   
def export_users_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'

    writer = csv.writer(response)
    writer.writerow(['Username','Email address','university','speciality','score','sections','string','date','Notcorrect'])

    users = User2.objects.all().values_list('user', 'email','university','speciality','score','sections','string','date','Notcorrect')
    for user in users:
        writer.writerow(user)

    return response

