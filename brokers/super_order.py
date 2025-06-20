"""
Manage Dhan Super Orders: place, modify, cancel, list.
Super Orders = ENTRY + TARGET + STOPLOSS bundled.
"""

from brokers.dhan_http import DhanHTTP


class SuperOrder:
    def __init__(self, dhan: DhanHTTP):
        self.dhan = dhan

    def list(self):
        return self.dhan.get("/super/orders")

    def place(self, security_id: str, exchange_segment: str, transaction_type: str,
              quantity: int, order_type: str, product_type: str, price: float,
              target_price: float, stop_loss_price: float, trailing_jump: float = 0.0,
              tag: str = None):
        
        if not all([security_id, exchange_segment, transaction_type, quantity,
                    order_type, product_type, price, target_price, stop_loss_price]):
            raise ValueError("Missing required fields for super order.")

        if price <= 0 or target_price <= 0 or stop_loss_price <= 0:
            raise ValueError("All leg prices must be > 0.")

        tx = transaction_type.upper()
        if tx == "BUY" and not (target_price > price and stop_loss_price < price):
            raise ValueError("For BUY: Target must be > price, SL < price.")
        if tx == "SELL" and not (target_price < price and stop_loss_price > price):
            raise ValueError("For SELL: Target must be < price, SL > price.")

        payload = {
            "transactionType": tx,
            "exchangeSegment": exchange_segment.upper(),
            "productType": product_type.upper(),
            "orderType": order_type.upper(),
            "securityId": security_id,
            "quantity": int(quantity),
            "price": float(price),
            "targetPrice": float(target_price),
            "stopLossPrice": float(stop_loss_price),
            "trailingJump": float(trailing_jump)
        }

        if tag:
            payload["correlationId"] = tag

        return self.dhan.post("/super/orders", payload)

    def modify(self, order_id: str, leg_name: str, order_type: str = None,
               quantity: int = 0, price: float = 0.0,
               target_price: float = 0.0, stop_loss_price: float = 0.0,
               trailing_jump: float = 0.0):
        
        if leg_name not in ("ENTRY_LEG", "TARGET_LEG", "STOP_LOSS_LEG"):
            raise ValueError("Invalid leg name.")

        payload = {"orderId": order_id, "legName": leg_name}

        if leg_name == "ENTRY_LEG":
            payload.update({
                "orderType": order_type,
                "quantity": quantity,
                "price": price,
                "targetPrice": target_price,
                "stopLossPrice": stop_loss_price,
                "trailingJump": trailing_jump
            })
        elif leg_name == "TARGET_LEG":
            payload["targetPrice"] = target_price
        elif leg_name == "STOP_LOSS_LEG":
            payload["stopLossPrice"] = stop_loss_price
            payload["trailingJump"] = trailing_jump

        return self.dhan.put(f"/super/orders/{order_id}", payload)

    def cancel(self, order_id: str, leg: str):
        if leg not in ("ENTRY_LEG", "TARGET_LEG", "STOP_LOSS_LEG"):
            raise ValueError("Invalid leg for cancellation.")
        return self.dhan.delete(f"/super/orders/{order_id}/{leg}")
