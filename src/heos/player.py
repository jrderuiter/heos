from dataclasses import dataclass

from .client import Client



@dataclass
class Player:
    id: int
    name: str
    host: str

    def __post_init__(self):
        self.client = Client(self.host)

    def __enter__(self):
        return self

    def __exit__(self, exec_type, exec_value, exec_traceback):
        self.client.close()

    @property
    def volume(self):
        response = self.client.send_command(
            "player/get_volume", params={"pid": self.id}
        )
        response.raise_for_result()
        return int(response.message_fields["level"])

    @volume.setter
    def volume(self, value: int):
        if not 0 <= value <= 100:
            raise ValueError("Volume must be between 0 and 100")

        response = self.client.send_command(
            "player/set_volume", params={"pid": self.id, "level": value}
        )
        response.raise_for_result()

    @property
    def mute(self):
        response = self.client.send_command("player/get_mute", params={"pid": self.id})
        response.raise_for_result()
        return response.message_fields["state"] == "on"

    @mute.setter
    def mute(self, value: bool):
        response = self.client.send_command(
            "player/set_mute",
            params={"pid": self.id, "state": "on" if value else "off"},
        )
        response.raise_for_result()


@dataclass
class PlayerGroup:
    id: int
    name: str
    host: str

    def __post_init__(self):
        self.client = Client(self.host)

    def __enter__(self):
        return self

    def __exit__(self, exec_type, exec_value, exec_traceback):
        self.client.close()

    @property
    def players(self):
        return self._get_players()

    def _get_players(self, role=None):
        response = self.client.send_command(
            "group/get_group_info", params={"gid": self.id}
        )
        response.raise_for_result()

        return {
            # Use own host for communicating with player for now.
            player["name"]: Player(
                id=player["pid"], name=player["name"], host=self.host
            )
            for player in response.payload["players"]
            if role is None or player["role"] == role
        }

    @property
    def leader(self):
        return next(iter(self._get_players(role="leader").values()))

    @property
    def members(self):
        return self._get_players(role="member")

    @property
    def volume(self):
        response = self.client.send_command("group/get_volume", params={"gid": self.id})
        response.raise_for_result()
        return int(response.message_fields["level"])

    @volume.setter
    def volume(self, value: int):
        if not 0 <= value <= 100:
            raise ValueError("Volume must be between 0 and 100")

        response = self.client.send_command(
            "group/set_volume", params={"gid": self.id, "level": value}
        )
        response.raise_for_result()

    @property
    def mute(self):
        response = self.client.send_command("group/get_mute", params={"gid": self.id})
        response.raise_for_result()
        return response.message_fields["state"] == "on"

    @mute.setter
    def mute(self, value: bool):
        response = self.client.send_command(
            "group/set_mute",
            params={"gid": self.id, "state": "on" if value else "off"},
        )
        response.raise_for_result()
