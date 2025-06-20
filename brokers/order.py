"""
Handles all order operations (place, modify, cancel, list) with Dhan API.
Designed to be GPT-callable and connected to Messenger or TagRouter.
"""

from dhan_http import DhanHTTP


class Order:
    def __init__(self, dhan: DhanHTTP):
        self.dhan = dhan

    def list_orders(self):
        return self.dhan.get("/orders")

    def get_by_id(self, order_id: str):
        return self.dhan.get(f"/orders/{order_id}")

    def get_by_correlation(self, correlation_id: str):
        return self.dhan.get(f"/orders/external/{correlation_id}")

    def cancel(self, order_id: str):
        return self.dhan.delete(f"/orders/{order_id}")

    def modify(self, order_id: str, order_type: str, leg_name: str, quantity: int,
               price: float, trigger_price: float, disclosed_quantity: int, validity: str):
        payload = {
            "orderId": str(order_id),
            "orderType": order_type,
            "legName": leg_name,
            "quantity": quantity,
            "price": price,
            "disclosedQuantity": disclosed_quantity,
            "triggerPrice": trigger_price,
            "validity": validity
        }
        return self.dhan.put(f"/orders/{order_id}", payload)

    def place(self, security_id: str, exchange_segment: str, transaction_type: str,
              quantity: int, order_type: str, product_type: str, price: float,
              trigger_price: float = 0.0, disclosed_quantity: int = 0,
              after_market_order: bool = False, validity: str = "DAY",
              amo_time: str = "OPEN", bo_profit_value=None, bo_stop_loss_value=None,
              tag: str = None, slicing: bool = False):
        
        if after_market_order and amo_time not in ['OPEN', 'OPEN_30', 'OPEN_60']:
            raise Exception("Invalid amo_time. Use: OPEN, OPEN_30, OPEN_60")

        payload = {
            "transactionType": transaction_type.upper(),
            "exchangeSegment": exchange_segment.upper(),
            "productType": product_type.upper(),
            "orderType": order_type.upper(),
            "validity": validity.upper(),
            "securityId": security_id,
            "quantity": int(quantity),
            "disclosedQuantity": int(disclosed_quantity),
            "price": float(price),
            "afterMarketOrder": after_market_order,
            "triggerPrice": float(trigger_price),
            "boProfitValue": bo_profit_value,
            "boStopLossValue": bo_stop_loss_value,
        }

        if tag:
            payload["correlationId"] = tag

        endpoint = "/orders/slicing" if slicing else "/orders"
        return self.dhan.post(endpoint, payload)

    def place_slice(self, *args, **kwargs):
        return self.place(*args, slicing=True, **kwargs)
