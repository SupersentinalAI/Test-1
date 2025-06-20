"""
Handles fund-related data retrieval and margin calculations from Dhan.
Fully GPT-readable and compatible with Messenger/brain logic.
"""

from dhan_http import DhanHTTP


class Funds:
    def __init__(self, dhan: DhanHTTP):
        self.dhan = dhan

    def get_fund_limits(self):
        """
        Returns:
            dict: Fund availability, margin used, collateral, etc.
        """
        return self.dhan.get("/fundlimit")

    def calculate_margin(self, security_id: str, exchange_segment: str,
                         transaction_type: str, quantity: int,
                         product_type: str, price: float, trigger_price: float = 0.0):
        """
        Args:
            security_id (str): Dhan security ID
            exchange_segment (str): e.g. NSE_EQ
            transaction_type (str): BUY / SELL
            quantity (int)
            product_type (str): CNC / INTRA
            price (float)
            trigger_price (float): Optional

        Returns:
            dict: Margin breakdown for given trade
        """
        payload = {
            "securityId": security_id,
            "exchangeSegment": exchange_segment.upper(),
            "transactionType": transaction_type.upper(),
            "quantity": int(quantity),
            "productType": product_type.upper(),
            "price": round(float(price), 2)
        }

        if trigger_price > 0:
            payload["triggerPrice"] = round(float(trigger_price), 2)

        return self.dhan.post("/margincalculator", payload)
