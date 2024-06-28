from django.urls import path
from . import consumers

ws_urlpatterns = [
    path('ws/sc/<str:roomname>',consumers.MySyncConsumer.as_asgi()),
]