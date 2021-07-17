from django.contrib import admin
from django.urls import path 
from . import views

app_name = 'shelf'

urlpatterns = [
    
    path('',views.dashboard,name='dashboard'),
    path('shelf/',views.index,name = 'index'),
    path('create/',views.create,name='create'),
    path('<int:shelf_id>/',views.detail,name='detail'),
    path('update/<int:shelf_id>/',views.update,name='update'),
    path('delete/<int:shelf_id>/',views.destroy,name='delete'),
    path('edit/<int:register_id>/',views.register_update,name='registerupdate'),
    path('remove/<int:register_id>/',views.register_delete,name='registerdelete'),
]