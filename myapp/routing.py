from django.urls import path
from . import consumers

ws_urlpatterns = [
    path('ws/sc/<str:roomname>/<str:name>',consumers.MySyncConsumer.as_asgi()),
]