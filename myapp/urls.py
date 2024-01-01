from django.urls import path 
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('create',views.create,name='create'),
    path('join',views.join,name='join'),
    path('play_on',views.play_on,name='play_on'),
]
