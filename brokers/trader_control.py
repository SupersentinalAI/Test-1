"""
Trader control functions, including kill switch activation for Dhan.
"""

from brokers.dhan_http import DhanHTTP


class TraderControl:
    def __init__(self, dhan: DhanHTTP):
        self.dhan = dhan

    def kill_switch(self, action: str):
        """
        Enable or disable the kill switch (trading halt).

        Args:
            action (str): 'activate' or 'deactivate'

        Returns:
            dict: API response from Dhan
        """
        action = action.strip().lower()
        if action not in ("activate", "deactivate"):
            return {"status": "failure", "remarks": "Invalid action. Use 'activate' or 'deactivate'."}

        endpoint = f"/killswitch?killSwitchStatus={action.upper()}"
        return self.dhan.post(endpoint)
