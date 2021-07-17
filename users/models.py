from typing import Sequence
from django.db import models
from django.db.models.fields import DateTimeField
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.
 

class Student(models.Model):

    gender_choice =[
        ('M','Male'),
        ('F','Female'),
        ('O','Other'),
    ]
    faculty_choice =[
        ('Sft','Software'),
        ('Cmp','Computer'),
    ]
    user = models.OneToOneField(User,on_delete=models.CASCADE,null=True)
    gender = models.CharField(max_length =10,choices=gender_choice,default='Male')
    faculty = models.CharField(max_length=15,choices=faculty_choice,null=True)
    total_books_due = models.PositiveIntegerField(default=0)
    reserved_books = models.PositiveIntegerField(default=0)
    



    

    def __str__(self):
        return self.user


