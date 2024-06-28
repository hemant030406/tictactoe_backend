from django.shortcuts import render
from rest_framework.response import Response
from .models import User
from rest_framework.decorators import api_view
from .serializers import UserSerializer
import jwt,datetime,pytz

IST = pytz.timezone('Asia/Kolkata') 

def home(request):
    return render(request,'index.html')

@api_view(['POST'])
def create(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'ok': True
        })

@api_view(['POST'])
def join(request):
    if request.method == 'POST':
        data = request.data
        roomname = data['name']
        code = data['code']

        room = User.objects.filter(name=roomname).first()

        if room is None:
            return Response({
                'ok': False
            })
        
        
        if not room.check_password(code):
            return Response({
                'ok': False
            })
        
        
        payload = {
            'id': room.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload,'secret',algorithm='HS256')

        res = Response()

        max_age = 60 * 60 * 24 * 15

        expiryDate= datetime.datetime.strftime(
            datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
            "%a, %d-%b-%Y %H:%M:%S GMT",
        )

        res.set_cookie(
            key='jwt',
            value=token,
            httponly=True,
            samesite='None',
            # domain=request.get_host().split(':')[0],
            max_age=max_age,
            expires=expiryDate,
            secure=True,
        )

        res.data = {
            'jwt': token,
            'ok': True
        }

        return res
    
@api_view(['GET'])
def auth(request):
    token = request.COOKIES.get('jwt')
    print(request.COOKIES)
    if not token:
        return Response({
            'ok': False
        })
    try:
        payload = jwt.decode(token,'secret',algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({
            'ok': False
        })
    
    room = User.objects.filter(id=payload['id']).first()

    if room is None:
        return Response({
            'ok': False
        })
    
    serializer = UserSerializer(room)

    return Response({
        'ok': True,
        'data': serializer.data
    })

@api_view(['POST'])
def delete_cook(request):
    data = request.data
    res = Response({
        'ok': True
    })
    res.delete_cookie(
        key='jwt',
        samesite='None'
    )
    room = User.objects.filter(name = data['room']).first()
    if room is not None:
        room.delete()
    return res