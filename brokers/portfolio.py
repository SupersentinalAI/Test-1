"""
Handles holdings, positions, and position conversion.
Clean, GPT-callable structure using DhanHTTP.
"""

from dhan_http import DhanHTTP


class Portfolio:
    def __init__(self, dhan: DhanHTTP):
        self.dhan = dhan

    def get_holdings(self):
        """
        Returns:
            dict: All delivery holdings from past sessions.
        """
        return self.dhan.get("/holdings")

    def get_positions(self):
        """
        Returns:
            dict: All intraday/F&O open positions for today.
        """
        return self.dhan.get("/positions")

    def convert_position(self, from_product_type: str, exchange_segment: str,
                         position_type: str, security_id: str, convert_qty: int,
                         to_product_type: str):
        """
        Converts a position (e.g. INTRA → CNC or vice versa).

        Args:
            from_product_type: "INTRA", "CNC", etc.
            exchange_segment: "NSE_EQ", "BSE_EQ", etc.
            position_type: "LONG" or "SHORT"
            security_id: Dhan security ID
            convert_qty: Quantity to convert
            to_product_type: "INTRA", "CNC", etc.

        Returns:
            dict: API response from Dhan
        """
        payload = {
            "fromProductType": from_product_type.upper(),
            "exchangeSegment": exchange_segment.upper(),
            "positionType": position_type.upper(),
            "securityId": security_id,
            "convertQty": int(convert_qty),
            "toProductType": to_product_type.upper()
        }
        return self.dhan.post("/positions/convert", payload)
