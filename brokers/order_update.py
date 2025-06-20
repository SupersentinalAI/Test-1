import asyncio
import websockets
import json


class OrderUpdate:
    def __init__(self, client_id, access_token):
        self.client_id = client_id
        self.access_token = access_token
        self.order_feed_wss = "wss://api-order-update.dhan.co"

    async def connect_order_update(self):
        async with websockets.connect(self.order_feed_wss) as websocket:
            auth_message = {
                "LoginReq": {
                    "MsgCode": 42,
                    "ClientId": str(self.client_id),
                    "Token": str(self.access_token)
                },
                "UserType": "SELF"
            }
            await websocket.send(json.dumps(auth_message))
            print(f"Sent subscribe message: {auth_message}")

            async for message in websocket:
                data = json.loads(message)
                await self.handle_order_update(data)

    async def handle_order_update(self, order_update):
        if order_update.get('Type') == 'order_alert':
            data = order_update.get('Data', {})
            order_id = data.get("orderNo")
            status = data.get("status", "Unknown")
            if order_id:
                print(f"Status: {status}, Order ID: {order_id}, Data: {data}")
            else:
                print(f"Order Update: {data}")
        else:
            print(f"Unknown message: {order_update}")

    def connect_sync(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.connect_order_update())
        except Exception as e:
            print(f"Error: {e}")
        finally:
            loop.close()
