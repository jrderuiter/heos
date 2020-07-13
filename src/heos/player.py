from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict

from .client import Client


class PlayState(Enum):
    """HEOS player state (e.g. play/pause/stop)."""

    play = "play"
    pause = "pause"
    stop = "stop"


@dataclass
class Player:
    """
    Class representing a HEOS player, used for issuing commands to specific players.
    """

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
    def volume(self) -> int:
        """Player volume."""

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
    def mute(self) -> bool:
        """Player mute status."""

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

    @property
    def now_playing(self) -> Dict[Any, Any]:
        """Media that is currently being played."""

        response = self.client.send_command(
            "player/get_now_playing_media", params={"pid": self.id}
        )
        response.raise_for_result()

        return response.payload

    def play(self):
        """Starts/resumes playback."""
        self._set_play_state(PlayState.play)

    def pause(self):
        """Pauses playback."""
        self._set_play_state(PlayState.pause)

    def stop(self):
        """Stops playback."""
        self._set_play_state(PlayState.stop)

    def _set_play_state(self, state: PlayState):
        response = self.client.send_command(
            "player/set_play_state", params={"pid": self.id, "state": state.value}
        )
        response.raise_for_result()

    def play_next(self):
        """Plays the next item in the player queue."""

        response = self.client.send_command(
            "player/play_next", params={"pid": self.id}
        )
        response.raise_for_result()

    def play_previous(self):
        """Plays the previous item in the player queue."""

        response = self.client.send_command(
            "player/play_previous", params={"pid": self.id}
        )
        response.raise_for_result()


@dataclass
class PlayerGroup:
    """
    Class representing a HEOS player group, used for issuing commands to the group.
    """

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
    def players(self) -> Dict[str, Player]:
        """All players in the group (keyed by name)."""
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
    def leader(self) -> Player:
        """Player that is leading the group."""
        return next(iter(self._get_players(role="leader").values()))

    @property
    def members(self) -> Dict[str, Player]:
        """Following members (e.g. non-leaders) in the group."""
        return self._get_players(role="member")

    @property
    def volume(self) -> int:
        """Group volume."""

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
    def mute(self) -> bool:
        """Group mute status."""

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

    @property
    def now_playing(self):
        """Media that is currently being played."""

        with self.leader as player:
            return player.now_playing

    def play(self):
        """Starts/resumes playback."""

        with self.leader as player:
            player.play()

    def pause(self):
        """Pauses playback."""

        with self.leader as player:
            player.pause()

    def stop(self):
        """Stops playback."""

        with self.leader as player:
            player.stop()

    def play_next(self):
        """Plays the next item in the queue."""

        with self.leader as player:
            player.play_next()

    def play_previous(self):
        """Plays the previous item in the queue."""

        with self.leader as player:
            player.play_previous()
