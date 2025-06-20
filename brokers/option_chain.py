"""
Option chain utilities for retrieving real-time strikes, OI, Greeks, IV, and expiry list.
Clean, GPT-callable structure using DhanHTTP.
"""

from dhan_http import DhanHTTP


class OptionChain:
    def __init__(self, dhan: DhanHTTP):
        self.dhan = dhan

    def get_chain(self, under_security_id: str, under_exchange_segment: str, expiry: str):
        """
        Get full option chain for a given underlying and expiry.

        Args:
            under_security_id (str): Dhan security ID of underlying (e.g., NIFTY)
            under_exchange_segment (str): e.g., NSE, NFO
            expiry (str): Expiry date (e.g., '2025-06-27')

        Returns:
            dict: Option chain data across all strikes
        """
        payload = {
            "UnderlyingScrip": under_security_id,
            "UnderlyingSeg": under_exchange_segment.upper(),
            "Expiry": expiry
        }
        return self.dhan.post("/optionchain", payload)

    def get_expiry_dates(self, under_security_id: str, under_exchange_segment: str):
        """
        Get available expiry dates for a given underlying.

        Args:
            under_security_id (str)
            under_exchange_segment (str)

        Returns:
            dict: List of available expiry dates
        """
        payload = {
            "UnderlyingScrip": under_security_id,
            "UnderlyingSeg": under_exchange_segment.upper()
        }
        return self.dhan.post("/optionchain/expirylist", payload)
