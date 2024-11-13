from django.urls import path
from .consumers import chatConsumers

websoket_urlpatterns = [
    path('ws/room/<room_id>/', chatConsumers.as_asgi()),
]
