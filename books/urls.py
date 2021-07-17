from users.views import reserved_books
from django.contrib import admin
from django.urls import path
from . import views
from .forms import Create,RegisterBook

app_name ='books'
urlpatterns = [
   
    path('',views.index,name='index'),
    path('<int:book_id>/',views.detail,name='detail'),
    path('create',views.create,name='create_books'),
    path('update/<int:book_id>',views.update,name='update'),
    path('delete/<int:book_id>/',views.delete,name='delete'),
    path('chooseshelf/<int:book_id>',views.choose_shelf,name='chooseshelf'),
    path('reserve/<int:book_id>',views.reserve_book,name='reserve'),
    path('reserved',views.reserved_books,name='reserved'),
    path('issue/<int:book_id>',views.issuebook,name='issue'),
    path('issuebook',views.issue,name='issuebook'),
    path('loadshelf/',views.load_shelf,name='loadshelf'),
    path('checkbook/',views.check_books,name="checkbooks"),
    path('issuedbooks/',views.showbooks,name='issuedbooks'),
    path('deposit/',views.depositbooks,name='depositbooks'),
    path('sendmessage',views.send_message,name='sendmessage'),
]