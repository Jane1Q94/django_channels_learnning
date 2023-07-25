from django.urls import re_path
from . import consumers

http_urlpatterns = [
    re_path('cm/test/$', consumers.HttpTest.as_asgi()),
    re_path('cm/longpoll/$', consumers.LongPollConsumer.as_asgi()),
    re_path('cm/sse/$', consumers.ServerSendEventsConsumer.as_asgi()),

]
