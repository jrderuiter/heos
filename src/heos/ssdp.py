#   Copyright 2014 Dan Krause
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from dataclasses import dataclass
import http.client
import io
import socket
from urllib.parse import urlparse


def discover(service, timeout=5, retries=1, mx=3):
    socket.setdefaulttimeout(timeout)

    responses = {}
    for _ in range(retries):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        message = SSDPMessage(service=service, mx=mx)
        sock.sendto(bytes(message), (message.address, message.port))

        while True:
            try:
                response = SSDPResponse.from_bytes(sock.recv(1024))
                responses[response.location] = response
            except socket.timeout:
                break

    return list(responses.values())


@dataclass
class SSDPMessage:
    service: str
    address: str = "239.255.255.250"
    port: int = 1900
    mx: int = 3

    def __str__(self):
        return "\r\n".join(
        [
            "M-SEARCH * HTTP/1.1",
            f"HOST: {self.address}:{self.port}",
            'MAN: "ssdp:discover"',
            f"ST: {self.service}",
            f"MX: {self.mx}",
            "",
            "",
        ]
    )

    def __bytes__(self):
        return str(self).encode("utf-8")


@dataclass
class SSDPResponse:
    location: str
    usn: str
    st: str
    cache: str

    class _FakeSocket(io.BytesIO):
        def makefile(self, *args, **kwargs):
            return self

    @classmethod
    def from_bytes(cls, response):
        r = http.client.HTTPResponse(cls._FakeSocket(response))
        r.begin()
        return cls(
            location=r.getheader("location"),
            usn=r.getheader("usn"),
            st=r.getheader("st"),
            cache=r.getheader("cache-control").split("=")[1],
        )

    @property
    def host(self):
        return urlparse(self.location).hostname


# Example:
# import ssdp
# ssdp.discover("roku:ecp")
