import json
import time
from datetime import datetime, timedelta
import urllib.parse
import jwt
import requests

from .exceptions import CubeTimeoutError, CubeError

DEFAULT_TOKEN_TTL = {"days": 1}
DEFAULT_CUBE_LOAD_REQUEST_TIMEOUT = 60
DEFAULT_CUBE_LOAD_WAITING_MAX_REQUESTS = 50
DEFAULT_CUBE_LOAD_WAITING_INTERVAL = 1
DEFAULT_CUBE_BASE_PATH = "cubejs-api"


class CubeJsClient:
    _server = None
    _base_path = None
    _secret = None
    _token = None
    _load_request_timeout = None
    _load_waiting_max_requests = None
    _load_waiting_interval = None
    _token_ttl = None
    _add_headers = {}

    def __init__(
        self,
        server,
        secret,
        base_path=DEFAULT_CUBE_BASE_PATH,
        load_request_timeout=DEFAULT_CUBE_LOAD_REQUEST_TIMEOUT,
        load_waiting_max_requests=DEFAULT_CUBE_LOAD_WAITING_MAX_REQUESTS,
        load_waiting_interval=DEFAULT_CUBE_LOAD_WAITING_INTERVAL,
        token_ttl=None,
        add_headers=None,
    ):
        self._server = server
        self._secret = secret
        self._base_path = base_path
        self._load_request_timeout = load_request_timeout
        self._load_waiting_max_requests = load_waiting_max_requests
        self._load_waiting_interval = load_waiting_interval
        if token_ttl:
            self._token_ttl = token_ttl
        else:
            self._token_ttl = DEFAULT_TOKEN_TTL
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
            self._token = jwt.encode({"exp": self._token_expiration}, self._secret, algorithm="HS256")
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
        return self.make_request("load", request_body, remaining_requests=self._load_waiting_max_requests)

    def sql(self, request_body):
        """
        Runs a sql request to Cube.js
        Returns:
            list
        """
        return self.make_request("sql", request_body, remaining_requests=self._load_waiting_max_requests)

    def make_request(self, server, request_body, remaining_requests=1):
        """
        Issues the request to cube.js
        Args:
            server: str - sql or load
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
            token = self.token
            try:
                url = f"{self._server}/{self._base_path}/v1/{server}?query={encoded_str_body}"
                remaining_requests -= 1
                response = requests.get(
                    url, timeout=self._load_request_timeout, headers={"Authorization": token, **self._add_headers}
                )
                if response.status_code != 200:
                    self.log(
                        "error",
                        "make_load_request.error_status_code",
                        remaining_requests=remaining_requests,
                        request_body=request_body,
                        status_code=response.status_code,
                        response=response.text,
                    )
                    if response.text:
                        raise CubeError("bad return status code: {} - {}".format(response.status_code, response.text))
                    else:
                        raise CubeError("bad return status code: {}".format(response.status_code))

                json_res = response.json()

                if "error" in json_res:
                    if json_res["error"] == "Continue wait":
                        time.sleep(self._load_waiting_interval)
                    else:
                        self.log(
                            "error",
                            "make_load_request.unrecognized_error",
                            remaining_requests=remaining_requests,
                            request_body=request_body,
                            status_code=response.status_code,
                            response=json_res,
                        )
                        raise CubeError("unrecognized error: {}".format(json_res["error"]))
                else:
                    self.log(
                        "info",
                        "make_load_request.success_response",
                        remaining_requests=remaining_requests,
                        request_body=request_body,
                        status_code=response.status_code,
                        response=json_res,
                    )
                    data_response = json_res["data"]
                    return data_response
            except requests.exceptions.RequestException:
                raise
        raise CubeTimeoutError()

    def log(self, level, msg, **kwargs):
        """
        Logging function hook that should be overridden if you want logging
        Issues the request to cube.js
        Args:
            level: str - the level to log at
            msg: str - the message
            kwargs: dict - any logging vars

        Returns:
            None
        """
        pass
