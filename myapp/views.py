from django.shortcuts import render,HttpResponse
from rest_framework.response import Response
from .models import Room
from rest_framework.decorators import api_view

# Create your views here.
def home(request):
    return HttpResponse('This is the home page')

@api_view(['POST'])
def create(request):
    if request.method == 'POST':
        data = request.data.dict()
        roomname = data['name']
        code = data['code']

        if Room.objects.filter(name=roomname).exists():
            return Response({
                "ok":"false",
                "message":"room already exists"
            })
        
        room = Room.objects.create(name=roomname,code=code)
        room.save()

        return Response({
            "ok":"true",
            "message":"room created"
        })

@api_view(['POST'])
def join(request):
    if request.method == 'POST':
        data = request.data.dict()
        roomname = data['name']
        code = data['code']

        room = Room.objects.filter(name=roomname,code=code).exists()
        
        if room:
            return Response({
                "ok":"true",
                "message":"entry allowed"
            }) 
        else:
            return Response({
                "ok":"false",
                "message":"either roomname or code is incorrect"
            }) 

@api_view(['POST','GET'])
def play_on(request):
    if request.method == 'POST':
        data = request.data.dict()
        roomname = data['name']
        arr = data['arr']

        room = Room.objects.get(name=roomname)
        room.arr = arr 
        room.save()

        return Response({
            'name': room.name,
            'code': room.code,
            'arr' : room.arr 
        })
    
    elif request.method == 'GET':
        data = request.data.dict()
        roomname = data['name']

        room = Room.objects.get(name=roomname)

        return Response({
            'name': room.name,
            'code': room.code,
            'arr' : room.arr 
        })
