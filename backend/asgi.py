import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import myapp.routing


application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': URLRouter(
        myapp.routing.ws_urlpatterns
    )
})

app = application
