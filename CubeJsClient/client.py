import json
import time
from datetime import datetime, timedelta
import urllib.parse
import jwt
import requests

from .exceptions import CubeTimeoutError, CubeError

TOKEN_TTL = {"days": 1}
CUBE_LOAD_REQUEST_TIMEOUT = 60
CUBE_LOAD_WAITING_MAX_REQUESTS = 50
CUBE_LOAD_WAITING_INTERVAL = 1


class CubeJsClient:
    _endpoint = None
    _secret = None
    _token = None
    _load_request_timeout = None
    _load_waiting_max_requests = None
    _load_waiting_interval = None
    _token_ttl = None
    _add_headers = {}

    def __init__(
        self,
        endpoint,
        secret,
        load_request_timeout=CUBE_LOAD_REQUEST_TIMEOUT,
        load_waiting_max_requests=CUBE_LOAD_WAITING_MAX_REQUESTS,
        load_waiting_interval=CUBE_LOAD_WAITING_INTERVAL,
        token_ttl=None,
        add_headers=None,
    ):
        self._endpoint = endpoint
        self._secret = secret
        self._load_request_timeout = load_request_timeout
        self._load_waiting_max_requests = load_waiting_max_requests
        self._load_waiting_interval = load_waiting_interval
        if token_ttl:
            self._token_ttl = token_ttl
        else:
            self._token_ttl = TOKEN_TTL
        if add_headers:
            self._add_headers = add_headers

    def _get_signed_token(self):
        """
        Handles signing the token
        Returns:
            string - token
        """
        now = datetime.now()
        if not self._token or self._token_expiration <= now:
            self._token_expiration = now + timedelta(**self._token_ttl)
            self._token = jwt.encode(
                {"exp": self._token_expiration}, self._secret, algorithm="HS256"
            )
        return self._token

    @property
    def token(self):
        return self._get_signed_token()

    def load(self, request_body):
        """
        Runs a load request to Cube.js
        Returns:
            list
        """
        return self.make_load_request(
            self.token, request_body, remaining_requests=self._load_waiting_max_requests
        )

    def make_load_request(self, token, request_body, remaining_requests=1):
        """
        Issues the request to cube.js
        Args:
            token: str - token
            request_body: dict - request to Cube.js
            remaining_requests: how many more requests to make

        Returns:
            list - results or raises CubeError
        """
        data_response = None
        str_body = json.dumps(request_body, separators=(",", ":"))
        encoded_str_body = urllib.parse.quote(str_body)
        while data_response is None and remaining_requests > 0:
            try:
                url = f"{self._endpoint}/cubejs-api/v1/load?query={encoded_str_body}"
                remaining_requests -= 1
                response = requests.get(
                    url,
                    timeout=CUBE_LOAD_REQUEST_TIMEOUT,
                    headers={"Authorization": token, **self._add_headers},
                )
                if response.status_code != 200:
                    if response.text:
                        raise CubeError(
                            "bad return status code: {} - {}".format(
                                response.status_code, response.text
                            )
                        )
                    else:
                        raise CubeError(
                            "bad return status code: {}".format(response.status_code)
                        )

                json_res = response.json()

                if "error" in json_res:
                    if json_res["error"] == "Continue wait":
                        time.sleep(self._load_waiting_interval)
                    else:
                        raise CubeError(
                            "unrecognized error: {}".format(json_res["error"])
                        )
                else:
                    data_response = json_res["data"]
                    return data_response
            except requests.exceptions.RequestException:
                raise
        raise CubeTimeoutError()
