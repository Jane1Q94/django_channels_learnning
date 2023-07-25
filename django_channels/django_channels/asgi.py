"""
ASGI config for django_channels project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from app.routing import websocket_urlpatterns
from app.routing_http import http_urlpatterns
from app.consumers import Worker1, Worker2

from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_channels.settings')

django_asgi_application = get_asgi_application()

application = ProtocolTypeRouter({
    # "http": django_asgi_application,
    "http": URLRouter(http_urlpatterns),
    "websocket": URLRouter(websocket_urlpatterns),
    "channel": ChannelNameRouter({
        "task1": Worker1.as_asgi(),
        "task2": Worker2.as_asgi()
    })
})
