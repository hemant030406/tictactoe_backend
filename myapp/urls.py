from django.urls import path 
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('create',views.create,name='create'),
    path('join',views.join,name='join'),
    path('auth',views.auth,name='auth'),
    path('delete',views.delete_cook,name='delete_cookie'),
    path('leave',views.leave,name='leave_room'),
]
