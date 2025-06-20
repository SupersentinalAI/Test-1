import os
from brokers.dhan_http import DhanHTTP

class Context:
    def __init__(
        self,
        openai_key=None,
        dhan_client_id=None,
        dhan_access_token=None,
    ):
        self.openai_key = openai_key or os.getenv("OPENAI_KEY")
        self.dhan_client_id = dhan_client_id or os.getenv("DHAN_CLIENT_ID")
        self.dhan_access_token = dhan_access_token or os.getenv("DHAN_ACCESS_TOKEN")
        self._dhan_http = None  # Lazy-loaded

    def get_dhan_http(self):
        if not self._dhan_http:
            if not self.dhan_client_id or not self.dhan_access_token:
                raise ValueError("❌ Missing Dhan credentials.")
            self._dhan_http = DhanHTTP(
                client_id=self.dhan_client_id,
                access_token=self.dhan_access_token
            )
        return self._dhan_http
