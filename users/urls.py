from django.contrib.auth import logout
from django.urls import path
from . import views



app_name = 'users'

urlpatterns = [
    path('',views.index,name='index'),
    path('profile/',views.profile,name='profile'),
    path('create/',views.create,name='create'),
    path('login/',views.login_request,name='login'),
    path('logout/',views.logout_view,name = 'logout'),
    path('password/',views.change_password,name='change'),
    path('reserved/<int:user_id>',views.reserved_books,name='reserved'),
    path('cancel/<int:book_id>',views.cancel_reservation,name='cancel'),
    path('borrowed/<int:user_id>',views.borrowed,name='borrowed'),
    path('fine',views.fine,name='fine'),
    path('pay',views.pay,name='pay'),
    path('verify',views.verify,name='verify'),
    
]


