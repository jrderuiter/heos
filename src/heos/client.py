from dataclasses import dataclass
import json
from telnetlib import Telnet
from typing import Any, Dict, List
from urllib.parse import urlencode, urlparse, parse_qsl

from cached_property import cached_property

from . import ssdp


class Client:
    def __init__(self, host):
        self.host = host
        self._telnet = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    @property
    def telnet(self):
        if self._telnet is None:
            self._telnet = Telnet(self.host, port=1255)
        return self._telnet

    def send_command(self, command: str, params: Dict[str, Any] = None):
        query = Query(command=command, params=params)
        self.telnet.write(bytes(query) + b"\n")

        response = Response.from_bytes(self.telnet.read_until(b"\r\n"))

        return response

    def close(self):
        if self._telnet is not None:
            self._telnet.close()
            self._telnet = None


@dataclass
class Query:
    command: str
    params: Dict[str, Any] = None

    def __str__(self):
        param_str = "?" + urlencode(self.params) if self.params else ""
        return f"heos://{self.command}{param_str}"

    def __bytes__(self):
        return str(self).encode("ascii")


@dataclass
class Response:
    command: str
    result: str
    message: str
    payload: Dict[str, Any]

    @classmethod
    def from_bytes(cls, bytes_):
        data = json.loads(bytes_.decode("utf-8"))
        return cls(
            command=data["heos"]["command"],
            result=data["heos"]["result"],
            message=data["heos"]["message"],
            payload=data.get("payload"),
        )

    @property
    def message_fields(self):
        return dict(parse_qsl(self.message))

    def raise_for_result(self):
        if self.result != "success":
            raise ValueError(f"Command {self.command} failed with error {self.message}")
