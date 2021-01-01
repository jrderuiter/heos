import json
from dataclasses import dataclass
from telnetlib import Telnet
from typing import Any, Dict
from urllib.parse import urlencode, parse_qsl


class Client:
    """
    Client for interacting with HEOS devices over telnet.

    Follows the specification in:
    http://rn.dmglobal.com/euheos/HEOS_CLI_ProtocolSpecification.pdf
    """

    def __init__(self, host: str):
        self.host = host
        self._telnet = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    @property
    def telnet(self):
        """Telnet client used for interacting with the device."""
        if self._telnet is None:
            self._telnet = Telnet(self.host, port=1255)
        return self._telnet

    def send_command(self, command: str, params: Dict[str, Any] = None):
        """Sends a heos command to the device, with optional parameters."""

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
    """Class respresenting a HEOS device command or query."""

    command: str
    params: Dict[str, Any] = None

    def __str__(self):
        param_str = "?" + urlencode(self.params) if self.params else ""
        return f"heos://{self.command}{param_str}"

    def __bytes__(self):
        return str(self).encode("ascii")


@dataclass
class Response:
    """Class representing a response from a HEOS device."""

    command: str
    result: str
    message: str
    payload: Dict[str, Any]

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        """Builds an instance from the given response bytes."""

        data = json.loads(bytes_.decode("utf-8"))
        return cls(
            command=data["heos"]["command"],
            result=data["heos"]["result"],
            message=data["heos"]["message"],
            payload=data.get("payload"),
        )

    @property
    def message_fields(self) -> Dict[str, str]:
        """Parsed message fields."""
        return dict(parse_qsl(self.message))

    def raise_for_result(self):
        """Raises an error if the response result was not successful."""

        if self.result != "success":
            raise ValueError(f"Command {self.command} failed with error {self.message}")
