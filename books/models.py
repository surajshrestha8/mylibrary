from django.db import models
from shelf.models import Shelf
from users.models import Student,User
# Create your models here.



class Book(models.Model):
    title = models.CharField(max_length=50,help_text='Enter the title of the book')
    isbn = models.CharField('ISBN',max_length=13,unique=True)
    author = models.CharField(max_length=50)
    publisher = models.CharField(max_length=50)
    shelf = models.ManyToManyField(Shelf,through='Register',related_name='shelf',null=True)
    is_available = models.BooleanField(default=True)

   


    def __str__(self):
        return self.title

class Register(models.Model):
    book = models.ForeignKey(Book,on_delete=models.PROTECT)
    shelf = models.ForeignKey(Shelf,on_delete=models.PROTECT)
    number_of_copies = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.book} - {self.shelf} - {self.number_of_copies}'

    

class Reservation(models.Model):
    reserved_by = models.ForeignKey(Student,on_delete=models.CASCADE)
    reserved_book = models.ForeignKey(Book,on_delete=models.CASCADE,null=True)
    shelf = models.ForeignKey(Shelf,on_delete=models.CASCADE,null=True)
    reserved_date = models.DateTimeField()



class Borrower(models.Model):

    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    book = models.ForeignKey(Book,on_delete=models.CASCADE)
    shelf = models.ForeignKey(Shelf,on_delete=models.CASCADE,null=True)
    issued_by = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    issue_date = models.DateTimeField()
    return_date = models.DateTimeField()
    is_deposited = models.BooleanField(default=False)
    
    def __str__(self):

        return f'{self.book.title} - {self.shelf} - {self.student.user.first_name}'

class Fine(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE,null=True)
    book = models.ForeignKey(Book,on_delete = models.CASCADE,null=True)
    amount = models.FloatField(default=0)
    is_paid = models.BooleanField(default=False)
    
    
