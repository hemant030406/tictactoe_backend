from django.shortcuts import render
from rest_framework.response import Response
from .models import Room
from rest_framework.decorators import api_view
from .serializers import UserSerializer
import jwt,datetime,pytz

IST = pytz.timezone('Asia/Kolkata') 

def home(request):
    return render(request,'index.html')

@api_view(['POST'])
def create(request):
    if request.method == 'POST':
        data = {
            'username':request.data['room'],
            'code': request.data['code']
        }
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'ok': True
            })
        else:
            msg = ''
            for field, errors in serializer.errors.items():
                if field == 'username':
                    msg = 'The room already exists.'
                else:
                    msg = 'Internal error'
            
            return Response({'ok': False, 'msg':msg, 'type': 'Warning'})

@api_view(['POST'])
def join(request):
    if request.method == 'POST':
        data = request.data
        roomname = data['room']
        code = data['code']
        username = data['name']

        room = Room.objects.filter(username=roomname).first()

        if room is None:
            return Response({
                'ok': False,
                'msg': "The room doesn't exist!",
                'type': 'Warning'
            })
        
        
        if not room.check_password(code):
            return Response({
                'ok': False,
                'msg': "Incorrect code!!!",
                'type': 'Danger'
            })
        
        if username in room.users:
            return Response({
                'ok': False,
                'msg': "Username already exists!!!",
                'type': 'Warning'
            })
        
        else:
            room.users.append(username)
        
        if len(room.turns.keys()) < 2:
            if len(room.turns.keys()) == 0:
                room.turns[username] = 'O'
            elif len(room.turns.keys()) == 1:
                room.turns[username] = 'X'

        room.save()
        
        payload = {
            'username':username,
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
    
@api_view(['POST','GET'])
def auth(request):
    token = request.COOKIES.get('jwt')
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
    
    room = Room.objects.filter(id=payload['id']).first()

    if room is None:
        return Response({
            'ok': False
        })
    
    serializer = UserSerializer(room)

    if request.method == 'POST':
        if request.data['name'] != payload['username']:
            return Response({
                'ok': False
            })

    return Response({
        'ok': True,
        'data': serializer.data,
        'username': payload['username']
    })

@api_view(['POST'])
def delete_cook(request):
    data = request.data
    room = Room.objects.filter(username = data['room']).first()

    if data['name'] not in room.turns.keys():
        return Response({
            'ok': False,
            'reason': "Only the current players can delete the room."
        })

    res = Response({
        'ok': True
    })
    res.delete_cookie(
        key='jwt',
        samesite='None'
    )
    if room is not None:
        room.delete()
    return res

@api_view(['POST'])
def leave(request):
    res = Response({
        'ok': True
    })
    res.delete_cookie(
        key='jwt',
        samesite='None'
    )
    return res
    