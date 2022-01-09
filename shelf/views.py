from django.core import paginator
from django.core.exceptions import RequestAborted
from django.http.response import HttpResponseBadRequest
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from .forms import ShelfForm,Update
from .models import Shelf 
from books.models import Book, Borrower,Register, Reservation
from django.db.models import Sum
from users.models import Student
from django.contrib import messages
from django.core.paginator import Paginator,EmptyPage
from users.decorators import allowed_users


# Create your views here.

def dashboard(request):
    number_of_books = Book.objects.count()
    number_of_students = Student.objects.count()
    shelves = Shelf.objects.all()
    number_of_issued_books = Borrower.objects.filter(is_deposited = False).count()
    number_of_reserved_books  = Reservation.objects.count()
    student = request.user


    context  = {
        'number_of_books':number_of_books,
        'number_of_students':number_of_students,
        'shelves':shelves,
        'number_of_reserved_books':number_of_reserved_books,
        'number_of_issued_books':number_of_issued_books,
      
    }

    return render(request,'shelf/dashboard.html',context)

@allowed_users(allowed_roles=['librarian'])
def index(request):
    shelves = Shelf.objects.all()  #retrieve all created shelves
    p = Paginator(shelves,5)
    page_num = request.GET.get('page',1)
    page = p.page(page_num)

    try:
        page = p.page(page_num)
    except EmptyPage:
        page = p.page(1)


    context = {
        'shelves':page
    }
    return render(request,'shelf/index.html',context)

@allowed_users(allowed_roles=['librarian'])
def create(request):
   
       
    
        if request.method == 'POST':
            shelf_name = request.POST.get('shelf_name',[])
            
            shelf = Shelf()
            shelf.shelf_name = shelf_name
            shelf.save()
            messages.success(request,'The shelf was created successfully')
            return redirect('shelf:index')

        return render(request,'shelf/create.html')

@allowed_users(allowed_roles=['librarian'])
def detail(request,shelf_id):
    shelf = Shelf.objects.get(id= shelf_id)
    books = Register.objects.filter(shelf_id=shelf_id)
    number_of_books = books.count()
    total = Register.objects.filter(shelf_id=shelf_id).aggregate(a=Sum('number_of_copies'))
    registers = total['a']
    
    context = {
        'shelf':shelf,
        'books':books,
        'number_of_books': number_of_books,
        'books':books,
        'registers':registers,
    }
    return render(request,'shelf/view.html',context)

    
@allowed_users(allowed_roles=['librarian'])
def update(request, shelf_id):
    old_shelf = get_object_or_404(Shelf,id = shelf_id)
    if request.method == 'POST':
        form = Update(request.POST or None,instance=old_shelf)
        if form.is_valid:
            form.save()
            messages.success(request,'The information about shelf was edited successfully')
            return redirect('shelf:index')
        else:
            return HttpResponse('Error occured')
    else:
        form = Update(instance=old_shelf)
        context = {
            'form':form,
        }
        return render(request,'shelf/update.html',context)  

@allowed_users(allowed_roles=['librarian'])
def destroy(request,shelf_id):
    shelf=Shelf.objects.get(pk= shelf_id)
    borrower = Borrower.objects.filter(shelf_id = shelf_id).count()
    print(borrower)
    if borrower > 0:
        messages.warning(request,'Cannot perform this action')
        return redirect('shelf:index')
    else:

        shelf.delete()
        messages.success(request,'The shelf was deleted successfully')
        return redirect('shelf:index')

@allowed_users(allowed_roles=['librarian'])
def register_update(request,register_id):
    register = Register.objects.get(id = register_id)
    
    if request.method == 'POST':
        number_of_copies = request.POST.get('number_of_copies')
        register.number_of_copies = number_of_copies
        register.save()
        messages.success(request,'Number of copies updated successfully')
        return redirect('shelf:index')
    
    return render(request,'shelf/registerupdate.html',{'register':register})

@allowed_users(allowed_roles=['librarian'])
def register_delete(request,register_id):

    register = Register.objects.get(id = register_id)
    book  = register.book.id
    borrower = Borrower.objects.filter(book_id = book,is_deposited = False).count()
    print(borrower)
    if borrower > 0:
        messages.warning(request,'This action cannot be performed')
        return redirect('shelf:index')
    else:


        register.delete()
        messages.success(request,"The book has been successfully removed from the shelf")
        return redirect('/')
    
    