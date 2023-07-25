import asyncio
from datetime import datetime
import json
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer
from channels.generic.http import AsyncHttpConsumer
from channels.exceptions import StopConsumer
from channels.consumer import SyncConsumer, AsyncConsumer
from asgiref.sync import async_to_sync


class ChatConsumer(WebsocketConsumer):

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.group_name = f"chat_{self.room_name}"

        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps({"message": message}))

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get("message")
        # self.send(text_data=json.dumps({"message": message}))

        async_to_sync(self.channel_layer.group_send)(
            self.group_name, {"type": "chat.message", "message": message}
        )


class AsyncChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.group_send(self.group_name, {"type": "chat.message", "message": message})

    async def chat_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))


class CustomSyncCustomer(SyncConsumer):

    def websocket_connect(self, event):
        self.send({
            "type": "websocket.accept"
        })

    def websocket_receive(self, event):
        self.send({
            "type": "websocket.send",
            "text": event["text"]
        })


class CustomAsyncCustomer(AsyncConsumer):
    async def websocket_connect(self, event):
        await self.send({
            "type": "websocket.accept"
        })

    async def websocket_receive(self, event):
        await self.send({
            "type": "websocket.send",
            "text": event["text"]
        })


# is not ok
class GroupTest(AsyncConsumer):
    groups = ["aibot"]

    async def websocket_connect(self, event):
        await self.send({"type": "websocket.accept"})

    async def websocket_receive(self, event):
        await self.channel_layer.group_send("aibot", {
            "type": "aibot.chat",
            "message": event["text"]
        })

    async def aibot_chat(self, event):
        await self.send({
            "type": "websocket.send",
            "text": event["message"]
        })

    async def websocket_disconnect(self, event):
        raise StopConsumer()


# is ok
class GroupTest2(AsyncWebsocketConsumer):
    groups = ["aibot"]

    async def connect(self):
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        await self.channel_layer.group_send("aibot", {
            "type": "aibot.group_chat",
            "message": text_data
        })

    async def aibot_group_chat(self, event):
        await self.send(text_data=event['message'])


# test JsonWebSocketConsumer
class JsonWebsocketTest(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def receive_json(self, content, **kwargs):
        await self.send_json({"content": content})


# test http consumer
class HttpTest(AsyncHttpConsumer):
    async def handle(self, body):
        await self.send_response(200, b"Your response is here!", headers=[
            (b'Content-Type', b'text/plain'),
        ])


# test Long poll
class LongPollConsumer(AsyncHttpConsumer):
    async def handle(self, body):
        await self.send_headers(headers=[
            (b'Content-Type', b'application/json')
        ])
        await self.send_body(b"hello world!\n", more_body=True)
        while True:
            await self.send_body(b"hello world!\n", more_body=True)
            await asyncio.sleep(0.5)

    async def chat_message(self, event):
        await self.send_body(json.dumps(event).encode("utf-8"))


# test sse
class ServerSendEventsConsumer(AsyncHttpConsumer):
    async def handle(self, body):
        await self.send_headers(headers=[
            (b'Cache-Control', b'no-cache'),
            (b'Content-Type', b'text/event-stream'),
            (b'Transfer-Encoding', b'chunked')
        ])

        while True:
            payload = f"data: {datetime.now().isoformat()}\n\n"
            await self.send_body(payload.encode('utf-8'), more_body=True)
            await asyncio.sleep(1)


# test worker
class Worker1(AsyncConsumer):
    async def worker_01(self, event):
        await asyncio.sleep(0.5)
        print(f'i am worker1, i receive {event}')


class Worker2(AsyncConsumer):
    async def worker_02(self, event):
        await asyncio.sleep(0.5)
        print(f'i am worker2, i receive {event}')
