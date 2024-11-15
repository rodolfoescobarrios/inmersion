from django.urls import re_path
from .consumers import chatConsumers

websoket_urlpatterns = [
    re_path(r'ws/room/(?P<room_id>\d+)/$', chatConsumers.ChatConsumer.as_asgi()),
]
