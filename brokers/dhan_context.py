class DhanContext:
    def __init__(self, client_id, access_token, ws_token=None):
        if not client_id or not access_token:
            raise ValueError("Dhan credentials missing.")
        self.client_id = client_id
        self.access_token = access_token
        self.ws_token = ws_token

    def get_client_id(self):
        return self.client_id

    def get_access_token(self):
        return self.access_token

    def get_ws_token(self):
        return self.ws_token

    def get_dhan_http(self):
        from .dhan_http import DhanHTTP
        return DhanHTTP(client_id=self.client_id, access_token=self.access_token)
