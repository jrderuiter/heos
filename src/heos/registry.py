from dataclasses import dataclass, asdict
from pathlib import Path

import yaml

from . import Client, Player, ssdp


class Registry:

    HEOS_URN = "urn:schemas-denon-com:device:ACT-Denon:1"

    def __init__(self, file_path=".heos"):
        self.file_path = file_path

        self._devices = {}

        if Path(self.file_path).exists():
            self.load()
        else:
            self.discover()

    @property
    def devices(self):
        return dict(self._devices)

    def discover(self) -> None:
        """Discovers players on the local network using SSDP."""

        ssdp_responses = ssdp.discover(self.HEOS_URN)

        devices = {}
        for ssdp_response in ssdp_responses:
            client = Client(ssdp_response.host)

            response = client.send_command("player/get_players")
            for entry in response.payload:
                devices[entry["name"]] = Device(
                    name=entry["name"],
                    model=entry["model"],
                    host=entry["ip"],
                    id=entry["pid"],
                )

        self._devices = devices
        self.save()

    def load(self):
        with open(self.file_path) as file_:
            config = yaml.safe_load(file_)
            device_config = config.get("devices", [])
        self._devices = {entry["name"]: Device(**entry) for entry in device_config}

    def save(self):
        config = {"devices": [asdict(device) for device in self._devices.values()]}
        with open(self.file_path, "w") as file_:
            yaml.dump(config, file_)

    def get_client(self, player_name):
        return Client(self.devices[player_name].host)

    def get_player(self, player_name):
        device = self.devices[player_name]
        return Player(id=device.id, name=device.name, client=Client(device.host))


@dataclass
class Device:
    name: str
    model: str
    host: str
    id: int
