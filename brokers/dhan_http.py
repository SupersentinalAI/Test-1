"""
Standalone class to interact with DhanHQ APIs using direct HTTP calls.

Supports: GET, POST, PUT, DELETE.
"""

import requests
import logging
from enum import Enum
from json import dumps as json_dumps, loads as json_loads


class DhanHTTP:
    class HttpResponseStatus(Enum):
        SUCCESS = 'success'
        FAILURE = 'failure'

    class HttpMethods(Enum):
        GET = 'GET'
        POST = 'POST'
        PUT = 'PUT'
        DELETE = 'DELETE'

    API_BASE_URL = 'https://api.dhan.co/v2'
    HTTP_DEFAULT_TIMEOUT = 60

    def __init__(self, client_id: str, access_token: str):
        self.client_id = client_id
        self.access_token = access_token
        self.base_url = self.API_BASE_URL
        self.timeout = self.HTTP_DEFAULT_TIMEOUT

        self.headers = {
            'access-token': self.access_token,
            'client-id': self.client_id,
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }

        self.session = requests.Session()

    def _send_request(self, method: HttpMethods, endpoint: str, payload=None):
        url = self.base_url + endpoint
        try:
            data = json_dumps(payload) if payload else None
            response = getattr(self.session, method.value.lower())(
                url,
                data=data,
                headers=self.headers,
                timeout=self.timeout
            )
            return self._parse_response(response)
        except Exception as e:
            logging.error(f"[DhanHTTP:{method.value}] ❌ Exception: {e}")
            return {
                "status": self.HttpResponseStatus.FAILURE.value,
                "remarks": str(e),
                "data": None
            }

    def _parse_response(self, response):
        try:
            content = json_loads(response.content)
            if response.ok:
                return {
                    "status": self.HttpResponseStatus.SUCCESS.value,
                    "remarks": "",
                    "data": content
                }
            else:
                return {
                    "status": self.HttpResponseStatus.FAILURE.value,
                    "remarks": content.get("errorMessage", "Unknown error"),
                    "data": None
                }
        except Exception as e:
            logging.warning(f"[DhanHTTP] ⚠️ Failed to parse response: {e}")
            return {
                "status": self.HttpResponseStatus.FAILURE.value,
                "remarks": str(e),
                "data": None
            }

    def get(self, endpoint: str):
        return self._send_request(self.HttpMethods.GET, endpoint)

    def post(self, endpoint: str, payload: dict):
        return self._send_request(self.HttpMethods.POST, endpoint, payload)

    def put(self, endpoint: str, payload: dict):
        return self._send_request(self.HttpMethods.PUT, endpoint, payload)

    def delete(self, endpoint: str):
        return self._send_request(self.HttpMethods.DELETE, endpoint)
