from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
    re_path(r"ws/chat_async/(?P<room_name>\w+)/$", consumers.AsyncChatConsumer.as_asgi()),
    re_path(r"ws/sync/$", consumers.CustomSyncCustomer.as_asgi()),
    re_path(r"ws/async/$", consumers.CustomAsyncCustomer.as_asgi()),
    re_path(r"ws/grouptest/$", consumers.GroupTest2.as_asgi()),
    re_path(r"ws/jsonwstest/$", consumers.JsonWebsocketTest.as_asgi()),
]
