from django.contrib import admin
from django.urls import path,include
# from myapp.views import Roomview

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/',include('rest_framework.urls')),
    path('',include('myapp.urls'))
]
