import asyncio
import websockets
import json


class OrderUpdate:
    def __init__(self, context):
        self.client_id = context.dhan_client_id
        self.access_token = context.dhan_access_token
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
            print(f"✅ Subscribed to Order Updates: {auth_message}")

            async for message in websocket:
                data = json.loads(message)
                await self.handle_order_update(data)

    async def handle_order_update(self, order_update):
        if order_update.get('Type') == 'order_alert':
            data = order_update.get('Data', {})
            order_id = data.get("orderNo")
            status = data.get("status", "Unknown")
            print(f"🟢 Order Update - Status: {status}, Order ID: {order_id}, Data: {data}")
        else:
            print(f"⚠️ Unknown message received: {order_update}")

    def connect_sync(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.connect_order_update())
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            loop.close()

    def describe(self):
        return {
            "module": "OrderUpdate",
            "client_id_present": bool(self.client_id),
            "connected": True
        }
