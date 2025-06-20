"""
Fetch historical candle data (OHLC + volume) for intraday and daily timeframes.
Directly uses DhanHTTP and is GPT-callable.
"""

import logging
from brokers.dhan_http import DhanHTTP


class Historical:
    def __init__(self, dhan: DhanHTTP):
        self.dhan = dhan

    def get_intraday(self, security_id: str, exchange_segment: str,
                     instrument_type: str, from_date: str, to_date: str, interval: int = 1):
        """
        Get minute-level intraday candles (max 5 trading days).

        Args:
            interval (int): Must be one of 1, 5, 15, 25, 60

        Returns:
            dict: Intraday candles
        """
        if interval not in [1, 5, 15, 25, 60]:
            err = "interval must be one of [1, 5, 15, 25, 60]"
            logging.error(f"[Historical] ❌ {err}")
            return {"status": "failure", "remarks": err, "data": ""}

        payload = {
            "securityId": security_id,
            "exchangeSegment": exchange_segment.upper(),
            "instrument": instrument_type.upper(),
            "interval": interval,
            "fromDate": from_date,
            "toDate": to_date
        }
        return self.dhan.post("/charts/intraday", payload)

    def get_daily(self, security_id: str, exchange_segment: str,
                  instrument_type: str, from_date: str, to_date: str, expiry_code: int = 0):
        """
        Get daily OHLC candles.

        Args:
            expiry_code (int): 0 = Spot, 1/2/3 = near/far expiry

        Returns:
            dict: Daily candles
        """
        if expiry_code not in [0, 1, 2, 3]:
            err = "expiry_code must be 0, 1, 2, or 3"
            logging.error(f"[Historical] ❌ {err}")
            return {"status": "failure", "remarks": err, "data": ""}

        payload = {
            "securityId": security_id,
            "exchangeSegment": exchange_segment.upper(),
            "instrument": instrument_type.upper(),
            "expiryCode": expiry_code,
            "fromDate": from_date,
            "toDate": to_date
        }
        return self.dhan.post("/charts/historical", payload)
