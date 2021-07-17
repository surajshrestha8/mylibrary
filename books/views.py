from datetime import date
from django.contrib.auth import login
from django.core.paginator import EmptyPage, Paginator
from django.db.models.fields import DateField
from django.http.response import JsonResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse,JsonResponse
from .forms import Create,UpdateBook,RegisterBook
from .models import Book, Register, Reservation, Borrower, Fine
from shelf.models import Shelf
from users.models import Student
from django.db.models import Sum
from shelf.forms import ShelfForm
from django.contrib.auth.decorators import login_required 
from django.contrib import messages
from django.utils.timezone import datetime, timedelta ,timezone
from django.core.mail import send_mail ,send_mass_mail
from .filters import BookFilter, StudentFilter

# Create your views here.

# to retrive all the books in the library
def index(request):
    books = Book.objects.all()
    number = Book.objects.count()
    
    shelves = Shelf.objects.all()

    book_filter = BookFilter(request.GET,queryset = books)
    books  = book_filter.qs 
    p = Paginator(books,5)
    page_num = request.GET.get('page',1)
    page = p.page(page_num)

    try:
        page = p.page(page_num)
    except EmptyPage:
        page = p.page(1)
    if number == 0:
        return HttpResponse('No books')
    else:
        return render(request,'books/index.html',{'books':page,'book_filter':book_filter,'shelves':shelves})


#function to create new books and keeping them into various shelves

def create(request):                       
    
    shelves = Shelf.objects.all() #retrieve all shelf objects 
    number = Shelf.objects.count() #count the number of objects in shelf
    if number == 0:
        return redirect('shelf:create')
    if request.method == 'POST':
       
        form = Create(request.POST)
        if form.is_valid():
            form.save()
           
            shelves = dict(request.POST).get('_shelf', [])
            book_counts = dict(request.POST).get('book_in_shelf', [])
           

            if not isinstance(book_counts, list):
                book_counts = [book_counts]
            if not isinstance(shelves, list):
                shelves = [shelves]

            for s,b in zip(shelves, book_counts):
                try:
                    shelf = Shelf.objects.get(shelf_name=s)
                except Exception as e:
                    continue

                try:
                    book_count_int = int(b)
                except:
                    book_count_int = 0

               
                r = Register(book=form.instance, shelf=shelf, number_of_copies=book_count_int)
                r.save()
                

                messages.success(request,'Book added successfully')
            
            
            return redirect('books:index')
        else:
            messages.warning(request,"Plese enter unique ISBN")
            return redirect('books:index')
    else:
        form = Create()
        shelf_form = ShelfForm()
        register_form = RegisterBook()
        return render(request,'books/books_create.html',{'form':form,'shelves':shelves, 'shelf_form': shelf_form, 'register_form': register_form})


# to view the information about an individual book

def detail(request,book_id):
    book = Book.objects.get(id=book_id)
    shelves = Register.objects.filter(book_id=book_id)
    total = Register.objects.filter(book_id=book_id).aggregate(a=Sum('number_of_copies'))
    registers = total['a']
    context = {
        'book': book,
        'shelves':shelves,
        'registers':registers,

    }
    return render(request,'books/view.html',context)


# to update the information about a book
def update(request,book_id):
    old_book = get_object_or_404(Book,id = book_id)
    if request.method =='POST':

        form = UpdateBook(request.POST or None, instance=old_book)
        if form.is_valid():
            form.save()
            return redirect('books:index')
        else:
            messages.warning(request,'Invalid data entered')
            return redirect('books:index')
    else:
        form = UpdateBook(instance=old_book)

        return render(request,'books/books_update.html',{'form':form})


# to delete a book
def delete(request,book_id):
    book = Book.objects.get(id = book_id)
    borrower = Borrower.objects.filter(book_id = book_id, is_deposited = False).count()
    print(borrower)

    if borrower > 0:
        messages.warning(request,'This book is borrowed,Cannot perform delete action!')
        return redirect('books:index')
    else:

        book.delete()
        messages.success(request,'The book was deleted successfully')
        return redirect('books:index')

def choose_shelf(request,book_id):
    book = Book.objects.get(id = book_id)
    reserve_date = request.POST.get('reserve_date')
    student = request.user.student
    
    register = Register.objects.filter(book_id  = book_id,number_of_copies__gt = 0)
    is_reserved = Reservation.objects.filter(reserved_by_id = request.user.student.id,reserved_book_id = book.id).count()
    if student.reserved_books >= 2:
        messages.warning(request,'You have exceeded maximum amount of books to reserve')
        return redirect('books:index')
    elif is_reserved > 0:
        messages.warning(request,'This book has been already reserved by you.')
        return redirect('books:index')
    else:
        
        return render(request,'books/chooseshelf.html',{'register':register,'book':book,'reserve_date':reserve_date})

# to reserve a particular book 
def reserve_book(request,book_id):
   
    book = Book.objects.get(id = book_id)
    student = request.user.student
    check_fine = Fine.objects.filter(student_id = student.id, is_paid = False).count()
    is_borrowed = Borrower.objects.filter(student_id = student.id,book_id = book.id, is_deposited = False).count()
    is_reserved = Reservation.objects.filter(reserved_by_id = student.id, reserved_book_id = book.id).count()


    if request.method == 'POST':
        reserve_date = request.POST.get('reserve_date')
        shelf = request.POST.get('shelf')
        if check_fine > 0:
            messages.warning(request,'You have pending fine. Please pay it first !')
            return redirect('books:index')
        else:
            if is_borrowed  > 0:
                messages.warning(request,'This book has been already issued to you')
                return redirect('books:index')

            elif is_reserved > 0:
                messages.warning(request,'This book is already reserved by you')
                return redirect('books:index')
            else:

                if student.reserved_books < 2:
                    reservation = Reservation()
                    reservation.reserved_by_id = student.id
                    reservation.reserved_book_id = book.id
                    reservation.shelf_id = shelf
                    reservation.reserved_date = reserve_date
                    reservation.save()
                    student.reserved_books = student.reserved_books + 1
                    student.save()
                    messages.success(request,"Your book has been reserved")
                    return redirect('books:index')
                else:
                    messages.warning(request,'You have exceeded maximum amount of books to reserve.')
                    return redirect('books:index')
       


def reserved_books(request):
    
    books = Reservation.objects.filter(reserved_date__gte = datetime.today())
    context = {
        'books':books,
    }
    return render(request,'books/reserved.html',context)

def issuebook(request,book_id):
    book = Reservation.objects.get(id = book_id)
    register = Register.objects.get(book_id = book.reserved_book_id,shelf_id = book.shelf_id)

    borrower = Borrower()
    borrower.book_id = book.reserved_book_id

    borrower.student_id = book.reserved_by_id
    borrower.shelf_id  = book.shelf_id
    borrower.issue_date = datetime.today()
    borrower.return_date = borrower.issue_date + timedelta(16)
    borrower.issued_by_id = request.user.id
    borrower.is_deposited = False
    borrower.save()
    register.number_of_copies = register.number_of_copies - 1
    register.save()
    book.delete()
    messages.success(request,'Book issued successfully')
    return redirect('books:index')




@login_required(login_url='users:login')
def issue(request):
    books = Book.objects.all()
    students = Student.objects.all()
    if request.method == 'POST':
        
        
        student = request.POST.get('student_username',)
        librarian = request.user
        ok = int(student)
        books_list = dict(request.POST).get('books_list[]',[])
        shelf_list = dict(request.POST).get('books_shelf[]',[])
      
        for b,s in zip(books_list,shelf_list):
            a = Book.objects.get(id = b)
            c = Shelf.objects.get(id = s)
            final = Register.objects.filter(book_id=b,shelf_id=s)
            print(final)
            for i in final:
                
                print(i.number_of_copies)
                print(type(i))
                print(a)

                student = Student.objects.get(id = ok)
                check_fine = Fine.objects.filter(student_id = student.id,is_paid=False).count()
                is_borrowed = Borrower.objects.filter(student_id = student.id, book_id =a.id,is_deposited = False).count()
            
                
                if check_fine > 0:
                    messages.warning(request,'This user has pending fine')
                    return redirect('books:issuebook')
                else:
                    if student.total_books_due>3:
                        messages.warning(request,"The user already has more than three books issued")
                        return redirect('books:issuebook')
                    else:
                        if is_borrowed > 0:
                            messages.warning(request,'This book has been already issued to this user')
                            return redirect('books:issuebook')
                        else:

                            student.total_books_due = student.total_books_due+1
                            i.number_of_copies = i.number_of_copies-1
                        
                            return_date = datetime.today() + timedelta(6)
                            borrower = Borrower(student = student, book=a,issue_date = datetime.today(), shelf = c, return_date = return_date, issued_by = librarian)
                            i.save()
                            email_address = [student.user.email]

                            print(type(email_address))
                            f_name = student.user.first_name
                            l_name = student.user.last_name
                            book_title = a.title 
                            print(book_title)
                            msg = "Hello" + ' '+ f_name + ' ' + l_name + '.'+ " You have been issued "+ book_title + ' book.'
                            print(msg) 
                            print(type(msg))
                            send_mail('Book issued',msg,'majorproject080@gmail.com',email_address,fail_silently=False)
                            student.save()
                            borrower.save() 
                
        messages.success(request,"Books issued successfully")       
        return redirect('books:index')            
               

    context = {
        'books':books,
        'students':students,
    }
    return render(request,'books/bookissue.html',context)


def load_shelf(request):
    books_id = request.GET.get('books')  # gets the id of the book selected in select dropdown
    shelves = Register.objects.filter(book_id = books_id,number_of_copies__gt = 0) # filters the shelves where that book is located and if there is atleast one book
    return render(request,'books/shelfoptions.html',{'shelves':shelves})

def check_books(request):
    student_id = request.GET.get('student_username')
    final_student_id = int(student_id)
    student = Student.objects.get(id = final_student_id)
    check_fine = Fine.objects.filter(student_id = student.id).count()
    print(check_fine)
    
    return JsonResponse(student.total_books_due,safe=False)


def showbooks(request):
    students = Student.objects.all()
    books = Book.objects.all()
    issuedbooks = Borrower.objects.all().exclude(is_deposited = True)
    student_filter = StudentFilter(request.GET,queryset = issuedbooks)
    issuedbooks = student_filter.qs
    p = Paginator(issuedbooks,10)
    page_num = request.GET.get('page',1)
    page = p.page(page_num)

    try:
        page = p.page(page_num)
    except EmptyPage:
        page = p.page(1)
    

    return render(request,'books/issuedindex.html',{'issuedbooks':page,'student_filter':student_filter,'students':students,'books':books})



def depositbooks(request):
    if request.method == 'POST':
        books = request.POST.getlist('id[]')
        
        for i in books:
            borrower = Borrower.objects.get(id= i)
            student = Student.objects.get(id = borrower.student.id)
            book = borrower.book.id
            shelf = borrower.shelf.id
            register = Register.objects.get(book_id = book, shelf_id = shelf)
            today = datetime.now(timezone.utc)
            difference  = today - borrower.return_date

            amount = 1

            if difference.days > 0:
                if difference.days > 5:
                    amount = amount*difference.days
                    fine = Fine(student = borrower.student, book = borrower.book, amount = amount, is_paid = False)
                    email_user = [borrower.student.user.email]
                    send_mail('Fine Alert','You have been charged','majorproject080@gmail.com',email_user,fail_silently=False)
                    fine.save()


            register.number_of_copies = register.number_of_copies + 1
            student.total_books_due = student.total_books_due - 1
            
            borrower.is_deposited = True
            register.save()
            student.save()
            borrower.save()
    
    
    messages.success(request,"Books deposited successfully")        
    return redirect('books:issuedbooks')         

def send_message(request):
    today  = datetime.today()
    end_date = today + timedelta(5)
    print(end_date)
    print(today)
    pending_deposit = Borrower.objects.filter(
        is_deposited = False,
        return_date__range = [today,end_date]
        
        
    )
    
    for i in pending_deposit:
    
        email_user = [i.student.user.email]
        send_mail('Alert','Please return your books in time','majorproject080@gmail.com',email_user)
        
    messages.success(request,'Mail sent successfully')
    return redirect('shelf:dashboard')
    
    