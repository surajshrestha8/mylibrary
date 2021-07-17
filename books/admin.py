from django.contrib import admin
from .models import Book,Register,Borrower,Fine
# Register your models here.

admin.site.register(Book)
admin.site.register(Register)
admin.site.register(Borrower)
admin.site.register(Fine)