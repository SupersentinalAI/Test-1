"""
Real-time 20-depth market data feed via Dhan WebSocket.
Fully async and GPT-ready.
"""

import asyncio
import struct
import websockets
import json
from datetime import datetime


class FullDepth:
    WSS_URL = 'wss://depth-api-feed.dhan.co/twentydepth'
    NSE = 1
    NSE_FNO = 2
    DEPTH_20 = 23

    def __init__(self, client_id: str, access_token: str, instruments: list):
        self.client_id = client_id
        self.access_token = access_token
        self.instruments = instruments
        self.ws = None
        self.loop = asyncio.get_event_loop()

    def run(self):
        self.loop.run_until_complete(self.connect())

    async def connect(self):
        url = f"{self.WSS_URL}?token={self.access_token}&clientId={self.client_id}&authType=2"
        self.ws = await websockets.connect(url)
        await self.subscribe()

    async def subscribe(self):
        batches = self._batch_instruments(self.instruments)
        for batch in batches:
            message = {
                "RequestCode": self.DEPTH_20,
                "InstrumentCount": len(batch),
                "InstrumentList": [
                    {
                        "ExchangeSegment": self._map_exchange(seg),
                        "SecurityId": token
                    } for seg, token in batch
                ]
            }
            await self.ws.send(json.dumps(message))

    async def receive(self):
        while True:
            data = await self.ws.recv()
            update = self._process(data)
            if update:
                print(update)

    def _map_exchange(self, code):
        return {
            1: "NSE_EQ",
            2: "NSE_FNO"
        }.get(code, str(code))

    def _batch_instruments(self, instruments, size=50):
        instruments = list(set(instruments))
        return [instruments[i:i + size] for i in range(0, len(instruments), size)]

    def _process(self, data):
        try:
            header = struct.unpack('<hBBiI', data[:12])
            msg_code = header[1]
            exchange = header[2]
            security_id = header[3]

            if msg_code not in [41, 51]:
                return None

            bids = self._parse_depth(data[12:], msg_code == 41)
            return {
                "type": "Bid" if msg_code == 41 else "Ask",
                "exchange": exchange,
                "security_id": security_id,
                "depth": bids
            }
        except Exception as e:
            return {"error": str(e)}

    def _parse_depth(self, data, is_bid=True):
        depth = []
        fmt = '<dII'
        size = struct.calcsize(fmt)

        for i in range(20):
            start = i * size
            end = start + size
            if end > len(data): break
            price, qty, orders = struct.unpack(fmt, data[start:end])
            depth.append({
                "price": price,
                "quantity": qty,
                "orders": orders
            })
        return depth
