import asyncio
import websockets
import struct
from datetime import datetime
from collections import defaultdict
import json


class MarketFeed:
    market_feed_wss = 'wss://api-feed.dhan.co'

    IDX = 0
    NSE = 1
    NSE_FNO = 2
    NSE_CURR = 3
    BSE = 4
    MCX = 5
    BSE_CURR = 7
    BSE_FNO = 8

    Ticker = 15
    Quote = 17
    Depth = 19
    Full = 21

    def __init__(self, client_id, access_token, instruments, version='v1'):
        self.client_id = client_id
        self.access_token = access_token
        self.instruments = instruments
        self.version = version
        self.ws = None
        self.loop = asyncio.get_event_loop()
        self.is_authorized = False
        self.data = ""

    def run_forever(self):
        self.loop.run_until_complete(self.connect())

    def get_data(self):
        return self.loop.run_until_complete(self.get_instrument_data())

    def close_connection(self):
        return self.loop.run_until_complete(self.disconnect())

    async def connect(self):
        if not self.ws or self.ws.state == websockets.protocol.State.CLOSED:
            if self.version == 'v1':
                self.ws = await websockets.connect(MarketFeed.market_feed_wss)
                await self.authorize()
            elif self.version == 'v2':
                url = f"{MarketFeed.market_feed_wss}?version=2&token={self.access_token}&clientId={self.client_id}&authType=2"
                self.ws = await websockets.connect(url)
            await self.subscribe_instruments()

    async def authorize(self):
        if self.version != 'v1':
            self.is_authorized = True
            return
        api_access_token = self.access_token.encode('utf-8').ljust(500, b'\0')
        client_id = self.client_id.encode('utf-8').ljust(30, b'\0')
        dhan_auth = b'\0' * 50
        payload = api_access_token + b"2P"
        header = struct.pack('<bH30s50s', 11, 83 + len(payload), client_id, dhan_auth)
        await self.ws.send(header + payload)
        self.is_authorized = True

    async def subscribe_instruments(self):
        instrument_batches = self._process_batches(self.instruments)
        for req_code, batches in instrument_batches.items():
            for batch in batches:
                if self.version == 'v2':
                    msg = {
                        "RequestCode": int(req_code),
                        "InstrumentCount": len(batch),
                        "InstrumentList": [
                            {
                                "ExchangeSegment": self._exchange_name(ex),
                                "SecurityId": token
                            } for ex, token in batch
                        ]
                    }
                    await self.ws.send(json.dumps(msg))
                else:
                    packet = self._create_packet(batch, int(req_code))
                    await self.ws.send(packet)

    async def get_instrument_data(self):
        response = await self.ws.recv()
        return self._parse_response(response)

    async def disconnect(self):
        if self.ws:
            if self.version == 'v2':
                await self.ws.send(json.dumps({"RequestCode": 12}))
                header = self._header(12, 83)
                await self.ws.send(header)

    def _exchange_name(self, code):
        return {
            0: "IDX_I", 1: "NSE_EQ", 2: "NSE_FNO", 3: "NSE_CURRENCY",
            4: "BSE_EQ", 5: "MCX_COMM", 7: "BSE_CURRENCY", 8: "BSE_FNO"
        }.get(code, str(code))

    def _process_batches(self, tuples_list, batch_size=100):
        result = defaultdict(list)
        for tup in tuples_list:
            ex, token = tup if len(tup) == 2 else tup[:2]
            req_type = tup[2] if len(tup) == 3 else 15
            result[str(req_type)].append((ex, token))
        return {
            k: [v[i:i+batch_size] for i in range(0, len(v), batch_size)]
            for k, v in result.items()
        }

    def _create_packet(self, instruments, req_code):
        header = self._header(req_code, 83 + 4 + len(instruments) * 21)
        num_inst = struct.pack('<I', len(instruments))
        info = b''.join(struct.pack('<B20s', ex, str(token).encode().ljust(20, b'\0')) for ex, token in instruments)
        padding = b''.join(struct.pack('<B20s', 0, b'') for _ in range(100 - len(instruments)))
        return header + num_inst + info + padding

    def _header(self, code, length):
        client = self.client_id.encode('utf-8').ljust(30, b'\0')
        dhan = b'\0' * 50
        return struct.pack('<bH30s50s', code, length, client, dhan)

    def _parse_response(self, data):
        first = struct.unpack('<B', data[0:1])[0]
        if first == 2:
            return self._parse_ticker(data)
        elif first == 3:
            return self._parse_depth(data)
        elif first == 4:
            return self._parse_quote(data)
        elif first == 5:
            return self._parse_oi(data)
        elif first == 8:
            return self._parse_full(data)

    def _parse_ticker(self, data):
        d = struct.unpack('<BHBIfI', data[0:16])
        return {
            "type": "Ticker",
            "exchange_segment": d[2],
            "security_id": d[3],
            "LTP": round(d[4], 2),
            "LTT": datetime.utcfromtimestamp(d[5]).strftime('%H:%M:%S')
        }

    def _parse_depth(self, data):
        d = struct.unpack('<BHBIf100s', data[0:112])
        depth_data = d[5]
        depth = []
        for i in range(5):
            pkt = struct.unpack('<IIHHff', depth_data[i*20:(i+1)*20])
            depth.append({
                "bid_qty": pkt[0], "ask_qty": pkt[1],
                "bid_orders": pkt[2], "ask_orders": pkt[3],
                "bid_price": round(pkt[4], 2), "ask_price": round(pkt[5], 2)
            })
        return {
            "type": "Depth",
            "exchange_segment": d[2],
            "security_id": d[3],
            "LTP": round(d[4], 2),
            "depth": depth
        }

    def _parse_quote(self, data):
        d = struct.unpack('<BHBIfHIfIIIffff', data[0:50])
        return {
            "type": "Quote",
            "exchange_segment": d[2],
            "security_id": d[3],
            "LTP": round(d[4], 2),
            "LTQ": d[5],
            "LTT": datetime.utcfromtimestamp(d[6]).strftime('%H:%M:%S'),
            "avg_price": round(d[7], 2),
            "volume": d[8],
            "total_sell_qty": d[9],
            "total_buy_qty": d[10],
            "open": round(d[11], 2),
            "close": round(d[12], 2),
            "high": round(d[13], 2),
            "low": round(d[14], 2)
        }

    def _parse_oi(self, data):
        d = struct.unpack('<BHBII', data[0:12])
        return {
            "type": "OI",
            "exchange_segment": d[2],
            "security_id": d[3],
            "OI": d[4]
        }

    def _parse_full(self, data):
        d = struct.unpack('<BHBIfHIfIIIIIIffff100s', data[0:162])
        depth_data = d[18]
        depth = []
        for i in range(5):
            pkt = struct.unpack('<IIHHff', depth_data[i*20:(i+1)*20])
            depth.append({
                "bid_qty": pkt[0], "ask_qty": pkt[1],
                "bid_orders": pkt[2], "ask_orders": pkt[3],
                "bid_price": round(pkt[4], 2), "ask_price": round(pkt[5], 2)
            })
        return {
            "type": "Full",
            "exchange_segment": d[2],
            "security_id": d[3],
            "LTP": round(d[4], 2),
            "LTQ": d[5],
            "LTT": datetime.utcfromtimestamp(d[6]).strftime('%H:%M:%S'),
            "avg_price": round(d[7], 2),
            "volume": d[8],
            "total_sell_qty": d[9],
            "total_buy_qty": d[10],
            "OI": d[11],
            "oi_day_high": d[12],
            "oi_day_low": d[13],
            "open": round(d[14], 2),
            "close": round(d[15], 2),
            "high": round(d[16], 2),
            "low": round(d[17], 2),
            "depth": depth
        }
