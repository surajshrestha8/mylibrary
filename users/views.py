from typing import ContextManager
from django import forms
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect
from django.shortcuts import render,redirect
from .models import Student
from books.models import Borrower, Reservation, Fine
from .forms import StudentCreateForm,StudentForm , LoginForm
from django.forms import ValidationError
from django.contrib import messages
from django.db.models import Sum
import requests 
import uuid
from django.core.mail import send_mail



from django.core.paginator import Paginator
from django.core import validators
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required ,permission_required
from django.contrib.auth.forms import AuthenticationForm,PasswordChangeForm
from django.contrib.auth import login,authenticate, logout, update_session_auth_hash
# Create your views here.
@login_required(login_url='users:login')
def profile(request):

    student_id = request.user.student.id
    print(student_id)
    books = Borrower.objects.filter(student_id = student_id)
    reserved_books = Reservation.objects.filter(reserved_by_id = student_id)
    
    print(reserved_books)
    context = {
        'books':books,
        'reserved_books':reserved_books,
    }
    return render(request,'students/profile.html',context)

@login_required(login_url='users:login')
def create(request):
    
        form = StudentCreateForm(request.POST or None)
        student_form = StudentForm(request.POST or None)
        if form.is_valid() and student_form.is_valid():
            user = form.save()
            student = student_form.save(commit=False)
            student.user = user
            email = request.POST.get('email')
            username = request.POST.get('username')
            email_user = [email]
            password1 = request.POST.get('password1')
            print(email)
            print(password1)
            message_to_student = """Hello! Your library account has been created. Please login with your following credentials:
                    Username:  """ + username + """
                    Password:  """ + password1
            
            student.save()
            send_mail('Library Account created!',message_to_student,'surajshre348@gmail.com',email_user,fail_silently=False)
            messages.success(request,'Profile created successfully')
            return redirect('users:login')
        
            
           
    
        
        student_form=StudentForm()
        context = {
            'form': form,
            'student_form':student_form,
        }
        return render(request,'students/create.html',context)




def login_request(request):
    if request.user.is_authenticated:
        return redirect('shelf:dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request,username=username,password=password)
            if user is not None:
                login(request,user)
                messages.success(request,'Logged in successfully')
                return redirect('shelf:dashboard')  
  
    form = LoginForm()
  
    return render(request,'students/login.html',context={'form':form})

def logout_view(request):
    logout(request)
    
    return redirect('users:login')
  
@login_required(login_url='users:login')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user ,request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request,user)
            return redirect('users:profile')
        
    else:
        form = PasswordChangeForm(request.user)
    return render(request,'students/change_password.html',{
        'form':form,
    })

def index(request):
    students = Student.objects.all()
    return render(request,'students/index.html',{'students':students})

def reserved_books(request,user_id):
   
    
    student_id = request.user.student.id
   
    students = Reservation.objects.filter(reserved_by_id=student_id)
    context = {
        'students':students,
    }
    
    return render(request,'students/reservedbooks.html',context)



def cancel_reservation(request,book_id):
    
    reserve = Reservation.objects.get(id=book_id)
    student = request.user.student


    student.reserved_books = student.reserved_books - 1  
    student.save()
    reserve.delete()
    
    messages.success(request,"The reservation is cancelled")
    return redirect('/')


def borrowed(request,user_id):

    student_id = request.user.student.id
    books = Borrower.objects.filter(student_id = student_id,is_deposited=False)
    print(books)
    fine = Fine.objects.filter(student_id= student_id , is_paid = False)
    total = fine.aggregate(a=Sum('amount'))
    total_amount = total['a']
    print(total_amount)
    return render(request,'students/borrowed.html',{'books':books,'total_amount':total_amount,'fine':fine})


def fine(request):
    student_id = request.user.student.id
    fine = Fine.objects.filter(student_id= student_id , is_paid = False)
    total = fine.aggregate(a=Sum('amount'))
    total_amount = total['a']
    for f in fine:
        print(f.amount)

    
    return render(request,'students/fine.html',{'fine':fine,'total_amount':total_amount})

def pay(request):
    student_id = request.user.student.id
    fine  = Fine.objects.filter(student_id = student_id, is_paid = False)
    total  = fine.aggregate(a = Sum('amount'))
    total_amount  = total['a']
    print(fine)
    print(total_amount)
    secret_id = uuid.uuid1()
    print(secret_id)
    context  = {
            'fine' : fine,
            'total_amount':total_amount,
            'student_id': student_id,
            'secret_id': secret_id,
    }
    return render(request,'students/esewa.html',context)

def verify(request):
    import xml.etree.ElementTree as ET
    oid= request.GET.get('oid')
    amt = request.GET.get('amt')
    refId = request.GET.get('refId')
    print(oid,amt,refId)

    
    url ="https://uat.esewa.com.np/epay/transrec"
    d = {
        'amt': amt,
        'scd': 'EPAYTEST',
        'rid': refId,
        'pid':oid,
    }
    resp = requests.post(url, d)
    root = ET.fromstring(resp.content)
    print(root)
    status = root[0].text.strip()
    print(status)
    student = (oid[-2:])
    s = int(student)
    print(type(s))
    email_user = [request.user.email]
    if status == 'Success':
        fine = Fine.objects.filter(student_id = s,is_paid = False)
        for f in fine:
            f.is_paid = True
            f.save()
    send_mail('Fine cleared','Thank you for paying your fine.Now you can reserve or borrow books from the library.','surajshre348@gmail.com',email_user,fail_silently=False)
    messages.success(request,'Your fine has been paid successfully')
    return redirect('/')





    

